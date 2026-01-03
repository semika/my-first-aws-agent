from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime
from strands import Agent
import logging
import boto3
import json
from botocore.exceptions import ClientError
from config import settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = FastAPI(title="Strands Agent Server", version="1.0.0")

# Initialize Strands agent.
# This is not used in the current implementation but kept for reference.
strands_agent = Agent()

class InvocationRequest(BaseModel):
    input: Dict[str, Any]

class InvocationResponse(BaseModel):
    output: Dict[str, Any]

# Claude invocation function
def invoke_model_claude(user_message):
    # Use the native inference API to send a text message to Anthropic Claude.

    # Create a Bedrock Runtime client in the AWS Region of your choice.
    bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

    # Set the model ID, e.g., Claude 3 Haiku.
    model_id = "anthropic.claude-haiku-4-5-20251001-v1:0"

    # Define the prompt for the model.
    prompt = user_message

    # Format the request payload using the model's native structure.
    native_request = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 512,
        "temperature": 0.5,
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}],
            }
        ],
    }

    # Convert the native request to JSON.
    request = json.dumps(native_request)

    try:
        # Invoke the model with the request.
        response = bedrock.invoke_model(modelId=model_id, body=request)

    except (ClientError, Exception) as e:
        print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
        exit(1)

    # Decode the response body.
    model_response = json.loads(response["body"].read())

    # Extract and print the response text.
    response_text = model_response["content"][0]["text"]
    print(response_text)

    return response_text




# Amazon Titan invocation function
def invoke_model_titan(user_message):

    logger.info(f"Invoking model 'amazon.titan-text-express-v1' with body: {user_message}")

    bedrock = boto3.client(service_name = 'bedrock-runtime', region_name = 'us-east-1')
    
    try:

        model_id = "amazon.titan-text-express-v1"
        body = json.dumps({
            "inputText": user_message,
            "textGenerationConfig": {
                "maxTokenCount": 3072,
                "stopSequences": [],
                "temperature": 0.7,
                "topP": 0.9
            }
        })
    
        response = bedrock.invoke_model(
            modelId=model_id,
            body=body,
            contentType='application/json',
            accept='application/json'
        )
        response_body_json = json.loads(response['body'].read().decode('utf-8'))
        output = response_body_json["results"][0]["outputText"]

        return output
    
    except (ClientError, Exception) as e:
        logging.error(e)
        return None
    
@app.post("/invocations", response_model=InvocationResponse)
async def invoke_agent(request: InvocationRequest):
    try:
        user_message = request.input.get("prompt", "")
        if not user_message:
            raise HTTPException(
                status_code=400, 
                detail="No prompt found in input. Please provide a 'prompt' key in the input."
            )

        #result = strands_agent(user_message)
        result = invoke_model_titan(user_message);
        #result = invoke_model_claude(user_message)
        response = {
            "message": result,
            "timestamp": datetime.utcnow().isoformat()
        }

        return InvocationResponse(output=response)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent processing failed: {str(e)}")

def invoke_as_user(user_id, session_id, prompt):
    try:
        agent_core_client = boto3.client('bedrock-agentcore', region_name='us-east-1')
        payload = json.dumps({
            "input": {"prompt": prompt}
        })

        response = agent_core_client.invoke_agent_runtime( 
            agentRuntimeArn=settings.agent_arn,
            runtimeSessionId = session_id,  # Must be 33+ chars
            payload = payload,
            qualifier="DEFAULT"
        )

        # For detail list of all the supported parameters for invoke_agent_runtime, refer to:
        # https://docs.aws.amazon.com/bedrock-agentcore/latest/APIReference/API_InvokeAgentRuntime.html

        response_body = response['response'].read()
        response_data = json.loads(response_body)
        print("Agent Response:", response_data)
        return response_data
        
    except Exception as e:
        print(f"Error invoking Agent Runtime: {str(e)}")
        raise e


# This API end point for local testing only.
@app.post("/invoke-agent-as-user", response_model=InvocationResponse)        
async def invoke_agent_as_user(request: InvocationRequest) -> InvocationResponse:
    try:
        prompt = request.input.get("prompt", "")
        session_id = request.input.get("session_id")
        user_id = request.input.get("user_id")

        if (prompt is None or session_id is None or user_id is None):
            raise HTTPException(
                status_code=400, 
                detail="Missing required fields. Please provide 'prompt', 'session_id', and 'user_id' in the input."
            )
        response_data = invoke_as_user(user_id, session_id, prompt)

        return InvocationResponse(output=response_data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent API invocation failed: {str(e)}")

@app.get("/ping")
async def ping():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)