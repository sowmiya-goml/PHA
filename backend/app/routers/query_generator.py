
from fastapi import APIRouter, Query, HTTPException
import os
import json
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError

# Load environment variables from .env if present
load_dotenv()

router = APIRouter()

@router.get("/generate-query")
async def generate_patient_query(
    schema: str = Query(..., description="Database schema structure"),
    patient_id: str = Query(..., description="Patient ID to extract details for")
):
    """
    Generate a database query to extract all details of a particular patient.
    """
    # Basic validation
    if not schema or not schema.strip():
        raise HTTPException(status_code=400, detail="Schema parameter is required and cannot be empty")
    
    if not patient_id or not patient_id.strip():
        raise HTTPException(status_code=400, detail="Patient ID parameter is required and cannot be empty")
    
    try:
        # Get AWS credentials from environment
        aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY") 
        aws_region = os.getenv("AWS_DEFAULT_REGION", "ap-south-1")
        
        # Validate AWS credentials
        if not aws_access_key or not aws_secret_key:
            raise HTTPException(status_code=500, detail="AWS credentials not configured properly")
        
        # Initialize Bedrock client
        bedrock_client = boto3.client(
            "bedrock-runtime",
            region_name=aws_region,
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key
        )
        
        # Create prompt for Claude with specific formatting requirements
        prompt = f"""
You are a database expert. Generate a SQL query to extract ALL details of patient with ID '{patient_id}' from the given database schema.

Database Schema:
{schema}

Patient ID: {patient_id}

Requirements:
- Return a complete SQL query that retrieves ALL patient information
- Include JOINs across related tables if needed
- Use proper SQL syntax with correct keywords (SELECT, FROM, WHERE, JOIN, etc.)
- Do NOT use line breaks (\\n) or newline characters in the query
- Return the query as a single line with spaces between clauses
- Only return the SQL query, nothing else - no explanations or markdown
- Ensure the query is safe and uses proper WHERE clauses with parameterized conditions
- Use standard SQL syntax that works across different database systems
- Do NOT use reserved SQL keywords (like OR, ID, STATUS, DESC, ORDER, GROUP, etc.) as table aliases or column names
- Always use safe, descriptive table aliases (e.g., 'obs_res' instead of 'or', 'imm_det' instead of 'id', 'pat_info' instead of 'pi')
- Ensure that column names do not conflict by applying proper aliases where needed
- When using SELECT *, consider potential column name conflicts and alias tables appropriately
- Avoid ambiguous column references - always qualify columns with table aliases when joining multiple tables
- Use meaningful alias names that clearly identify the table (e.g., patients AS pat, observations AS obs, immunizations AS imm)

Example format: SELECT pat.*, obs.* FROM patients AS pat LEFT JOIN observations AS obs ON pat.patient_id = obs.patient_id WHERE pat.patient_id = '{patient_id}';
"""
        
        # Use the correct inference profile ARN that you have access to
        model_ids = [
            "arn:aws:bedrock:ap-south-1:422228628797:inference-profile/apac.anthropic.claude-3-5-sonnet-20240620-v1:0",  # Claude 3.5 Sonnet (APAC inference profile)
            "anthropic.claude-3-5-sonnet-20240620-v1:0",         # Claude 3.5 Sonnet (fallback direct model ID)
        ]
        
        response = None
        model_used = None
        
        for model_id in model_ids:
            try:
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
                model_used = model_id
                break
            except ClientError as e:
                print(f"Failed to use model {model_id}: {str(e)}")
                if "AccessDeniedException" in str(e) or "ValidationException" in str(e):
                    continue  # Try next model
                else:
                    raise e
            except Exception as e:
                print(f"Unexpected error with model {model_id}: {str(e)}")
                continue
        
        if not response:
            raise HTTPException(status_code=500, detail="No compatible Claude model available")
        
        # Parse response
        result = json.loads(response['body'].read())
        generated_query = result['content'][0]['text'].strip()
        
        # Clean up the generated query - remove line breaks and extra spaces
        generated_query = generated_query.replace('\n', ' ').replace('\r', ' ')
        # Remove multiple spaces and replace with single space
        import re
        generated_query = re.sub(r'\s+', ' ', generated_query).strip()
        
        # Remove any markdown code block formatting if present
        if generated_query.startswith('```sql'):
            generated_query = generated_query.replace('```sql', '').replace('```', '').strip()
        elif generated_query.startswith('```'):
            generated_query = generated_query.replace('```', '').strip()
        
        return {
            "generated_query": generated_query,
            "patient_id": patient_id,
            "model_used": model_used,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query generation failed: {str(e)}")


@router.get("/available-models")
async def list_available_models():
    """
    List available Bedrock models in your AWS account for debugging.
    """
    try:
        # Get AWS credentials from environment
        aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY") 
        aws_region = os.getenv("AWS_DEFAULT_REGION", "ap-south-1")
        
        # Initialize Bedrock client
        bedrock_client = boto3.client(
            "bedrock",  # Note: using bedrock, not bedrock-runtime
            region_name=aws_region,
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key
        )
        
        # List foundation models
        response = bedrock_client.list_foundation_models()
        
        # Filter for Anthropic models
        anthropic_models = []
        for model in response.get('modelSummaries', []):
            if 'anthropic' in model.get('modelId', '').lower():
                anthropic_models.append({
                    'modelId': model.get('modelId'),
                    'modelName': model.get('modelName'),
                    'providerName': model.get('providerName'),
                    'inputModalities': model.get('inputModalities'),
                    'outputModalities': model.get('outputModalities')
                })
        
        return {
            "available_anthropic_models": anthropic_models,
            "total_models": len(response.get('modelSummaries', [])),
            "region": aws_region
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list models: {str(e)}")


@router.get("/test-model-access")
async def test_model_access():
    """
    Test access to Claude models with a simple prompt.
    """
    try:
        # Get AWS credentials from environment
        aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY") 
        aws_region = os.getenv("AWS_DEFAULT_REGION", "ap-south-1")
        
        # Initialize Bedrock client
        bedrock_client = boto3.client(
            "bedrock-runtime",
            region_name=aws_region,
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key
        )
        
        # Test your specific inference profile ARN first
        test_models = [
            "arn:aws:bedrock:ap-south-1:422228628797:inference-profile/apac.anthropic.claude-3-5-sonnet-20240620-v1:0",  # Your Claude 3.5 Sonnet ARN
            "anthropic.claude-3-5-sonnet-20240620-v1:0",  # Claude 3.5 Sonnet (direct model ID)
        ]
        
        results = []
        
        for model_id in test_models:
            try:
                response = bedrock_client.invoke_model(
                    modelId=model_id,
                    contentType="application/json",
                    accept="application/json",
                    body=json.dumps({
                        "anthropic_version": "bedrock-2023-05-31",
                        "max_tokens": 100,
                        "temperature": 0.1,
                        "messages": [
                            {
                                "role": "user",
                                "content": "Say hello"
                            }
                        ]
                    })
                )
                
                result = json.loads(response['body'].read())
                results.append({
                    "model_id": model_id,
                    "status": "success",
                    "response": result['content'][0]['text'].strip()
                })
                
            except Exception as e:
                results.append({
                    "model_id": model_id,
                    "status": "failed",
                    "error": str(e)
                })
        


        return {
            "test_results": results,
            "region": aws_region,
            "note": "Models with 'AccessDeniedException' need access to be requested in AWS Bedrock console. Models with 'ValidationException' may need inference profiles."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")


@router.get("/list-inference-profiles")
async def list_inference_profiles():
    """
    List available inference profiles for Claude models.
    """
    try:
        # Get AWS credentials from environment
        aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY") 
        aws_region = os.getenv("AWS_DEFAULT_REGION", "ap-south-1")
        
        # Initialize Bedrock client
        bedrock_client = boto3.client(
            "bedrock",
            region_name=aws_region,
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key
        )
        
        # List inference profiles
        response = bedrock_client.list_inference_profiles()
        
        # Filter for Claude/Anthropic profiles
        claude_profiles = []
        for profile in response.get('inferenceProfileSummaries', []):
            if 'anthropic' in profile.get('inferenceProfileName', '').lower() or \
               'claude' in profile.get('inferenceProfileName', '').lower():
                claude_profiles.append({
                    'inferenceProfileId': profile.get('inferenceProfileId'),
                    'inferenceProfileName': profile.get('inferenceProfileName'),
                    'description': profile.get('description', ''),
                    'status': profile.get('status'),
                    'type': profile.get('type')
                })
        
        return {
            "claude_inference_profiles": claude_profiles,
            "total_profiles": len(response.get('inferenceProfileSummaries', [])),
            "region": aws_region
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list inference profiles: {str(e)}")
