import boto3
import json

try:
    agent_core_client = boto3.client('bedrock-agentcore', region_name='us-east-1')
    payload = json.dumps({
        "input": {"prompt": "Explain machine learning in simple terms"}
    })

    response = agent_core_client.invoke_agent_runtime(
        agentRuntimeArn='arn:aws:bedrock-agentcore:us-east-1:762002331286:runtime/strands_agent-00R962CU13',
        runtimeSessionId='dfmeoagmreaklgmrkleafremoigrmtesogmtrskhmtkrlshmt',  # Must be 33+ chars
        payload=payload,
        qualifier="DEFAULT"
    )

    response_body = response['response'].read()
    response_data = json.loads(response_body)
    print("Agent Response:", response_data)
except Exception as e:
    print(f"Error invoking Agent Runtime: {str(e)}")