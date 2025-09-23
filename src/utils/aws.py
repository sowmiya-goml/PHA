import json
from botocore.exceptions import BotoCoreError
import boto3
import os
from fastapi.responses import StreamingResponse
 
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
 
bedrock = boto3.client(
    "bedrock-runtime",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY
) if AWS_ACCESS_KEY and AWS_SECRET_KEY else boto3.client(
    "bedrock-runtime",
    region_name=AWS_REGION
)
 
def call_bedrock_summary(prompt: str):
    try:
        response = bedrock.invoke_model_with_response_stream(
            modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 6000,
                "temperature": 0.3,
                "messages": [{"role": "user", "content": prompt}]
            }),
            contentType="application/json",
            accept="application/json"
        )
 
        def stream_generator():
            for event in response["body"]:
                if "chunk" in event and "bytes" in event["chunk"]:
                    chunk_data = json.loads(event["chunk"]["bytes"])
                    content = chunk_data.get("delta", {}).get("text", "")
                    yield content
 
        return StreamingResponse(stream_generator(), media_type="text/plain")
 
    except BotoCoreError as e:
        raise Exception(f"Bedrock API call failed: {str(e)}")
 
