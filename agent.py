from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime
from strands import Agent
import logging
import boto3
import json
from botocore.exceptions import ClientError

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
        response = {
            "message": result,
            "timestamp": datetime.utcnow().isoformat()
        }

        return InvocationResponse(output=response)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent processing failed: {str(e)}")

@app.get("/ping")
async def ping():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)