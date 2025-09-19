"""Simple test for Bedrock LLM client without database dependency."""

import os
import sys
import asyncio
import json
import boto3
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Set environment variables from config
config_file = Path(__file__).parent / 'config' / '.env'
if config_file.exists():
    with open(config_file, 'r') as f:
        for line in f:
            if line.strip() and '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value


async def test_bedrock_direct():
    """Test Bedrock client directly without database dependencies."""
    
    print("🔍 Testing Bedrock LLM Client Directly")
    print("=" * 50)
    
    try:
        # Step 1: Check environment variables
        print("1. Checking AWS Configuration...")
        aws_key = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret = os.getenv('AWS_SECRET_ACCESS_KEY')
        aws_region = os.getenv('AWS_DEFAULT_REGION')
        
        print(f"   AWS_ACCESS_KEY_ID: {'SET' if aws_key else 'NOT SET'}")
        print(f"   AWS_SECRET_ACCESS_KEY: {'SET' if aws_secret else 'NOT SET'}")
        print(f"   AWS_DEFAULT_REGION: {aws_region or 'NOT SET'}")
        
        if not aws_key or not aws_secret:
            print("❌ AWS credentials are missing!")
            return
        
        # Step 2: Create Bedrock client
        print("\n2. Creating Bedrock Client...")
        try:
            bedrock_client = boto3.client(
                "bedrock-runtime",
                region_name=aws_region,
                aws_access_key_id=aws_key,
                aws_secret_access_key=aws_secret
            )
            print("   ✅ Bedrock client created successfully")
        except Exception as e:
            print(f"   ❌ Failed to create Bedrock client: {e}")
            return
        
        # Step 3: Test simple query generation
        print("\n3. Testing LLM Query Generation...")
        
        # Simple prompt for SQL generation
        prompt = """
        You are a SQL expert. Generate a simple SQL query for the following schema:
        
        Table: patients
        Columns: patient_id (VARCHAR), first_name (VARCHAR), last_name (VARCHAR)
        
        Generate a SELECT query to find a patient with patient_id = 'test-123'.
        Return only the SQL query, nothing else.
        """
        
        # Test with different model IDs
        model_ids = [
            "arn:aws:bedrock:ap-south-1:422228628797:inference-profile/apac.anthropic.claude-3-5-sonnet-20240620-v1:0",
            "anthropic.claude-3-5-sonnet-20240620-v1:0",
        ]
        
        for model_id in model_ids:
            try:
                print(f"   🔄 Trying model: {model_id}")
                
                response = bedrock_client.invoke_model(
                    modelId=model_id,
                    contentType="application/json",
                    accept="application/json",
                    body=json.dumps({
                        "anthropic_version": "bedrock-2023-05-31",
                        "max_tokens": 1000,
                        "temperature": 0.1,
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ]
                    })
                )
                
                response_body = json.loads(response['body'].read())
                generated_query = response_body['content'][0]['text']
                
                print(f"   ✅ Query generated successfully with {model_id}!")
                print(f"   Generated Query: {generated_query.strip()}")
                return  # Success, exit early
                
            except Exception as e:
                print(f"   ❌ Model {model_id} failed: {e}")
                continue
        
        print("   ❌ All models failed!")
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_bedrock_direct())