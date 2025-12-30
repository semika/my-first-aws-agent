import boto3

try:
    client = boto3.client('bedrock-agentcore-control', region_name='us-east-1')

    response = client.create_agent_runtime(
        agentRuntimeName='strands_agent',
        agentRuntimeArtifact={
            'containerConfiguration': {
                'containerUri': '762002331286.dkr.ecr.us-east-1.amazonaws.com/my-strands-agent:latest'
            }
        },
        lifecycleConfiguration={
            'idleRuntimeSessionTimeout': 900,  # 30 minutes
            'maxLifetime': 28800  # 4 hours
        },
        networkConfiguration={"networkMode": "PUBLIC"},
        roleArn='arn:aws:iam::762002331286:role/AgentRuntimeRole'
    )

    print(f"Agent Runtime created successfully!")
    print(f"Agent Runtime ARN: {response['agentRuntimeArn']}")
    print(f"Status: {response['status']}")

except Exception as e:
    print(f"Error creating Agent Runtime: {str(e)}")    