### Introduction

This python projects creates an agent and deploy it inside AWS agent core runtime.
Using Amazon titan text model.

### The reference documentation

https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/getting-started-custom.html

### How to start Fast API applicaiton locally
> uv run uvicorn agent:app --host 0.0.0.0 --port 8080

### How to run Fast API end poing via Postman

Set the request as POST with the URL 'http://localhost:8080/invocations'.

Json data payload should be as follows.
```
{
    "input": {"prompt": "Explain machine learning in simple terms"}
}
```

### Deploying the agent into AWS ECR

1. Create a ECR repository

> aws ecr create-repository --repository-name my-strands-agent --region us-east-1

2. Loginto ECR

> aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 762002331286.dkr.ecr.us-east-1.amazonaws.com

3. Build the docker image and publish it to ECR

> docker buildx build --platform linux/arm64 -t 762002331286.dkr.ecr.us-east-1.amazonaws.com/my-strands-agent:latest --push .

4. Verify that the image was published to ECR properly.

> aws ecr describe-images --repository-name my-strands-agent --region us-east-1