"""Test Bedrock LLM query generation directly."""

import os
import sys
import asyncio
import json
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

from pha.db.session import DatabaseManager
from pha.services.bedrock_service import BedrockService


async def test_bedrock_query_generation():
    """Test Bedrock LLM query generation step by step."""
    
    print("🔍 Testing Bedrock LLM Query Generation")
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
        
        # Step 2: Initialize services
        print("\n2. Initializing Services...")
        db_manager = DatabaseManager()
        
        print("   Connecting to database...")
        db_connected = await db_manager.connect()
        if not db_connected:
            print("   ⚠️ Database connection failed, but continuing with Bedrock test...")
        else:
            print("   ✅ Database connected")
        
        bedrock_service = BedrockService(db_manager)
        print("   ✅ Services initialized")
        
        # Step 3: Test Bedrock client creation
        print("\n3. Testing Bedrock Client...")
        try:
            bedrock_client = bedrock_service._get_bedrock_client()
            print("   ✅ Bedrock client created successfully")
        except Exception as e:
            print(f"   ❌ Failed to create Bedrock client: {e}")
            return
        
        # Step 4: Test query generation with simple schema
        print("\n4. Testing Query Generation...")
        
        # Simple test schema
        test_schema = {
            "database_info": {
                "name": "test_db",
                "type": "postgresql"
            },
            "tables": [
                {
                    "name": "patients",
                    "type": "table",
                    "columns": [
                        {"name": "patient_id", "type": "VARCHAR(50)"},
                        {"name": "first_name", "type": "VARCHAR(100)"},
                        {"name": "last_name", "type": "VARCHAR(100)"}
                    ]
                }
            ]
        }
        
        test_patient_id = "test-123"
        
        print(f"   Using test patient ID: {test_patient_id}")
        print("   Calling generate_healthcare_query...")
        
        result = bedrock_service.generate_healthcare_query(
            schema=test_schema,
            patient_id=test_patient_id,
            query_type="basic"
        )
        
        print(f"\n5. Query Generation Result:")
        print(f"   Status: {result.get('status', 'unknown')}")
        
        if result.get('status') == 'success':
            print("   ✅ Query generated successfully!")
            print(f"   Generated Query: {result.get('generated_query', 'N/A')}")
            print(f"   Model Used: {result.get('model_used', 'N/A')}")
        elif result.get('status') == 'failed':
            print(f"   ❌ Query generation failed: {result.get('error', 'Unknown error')}")
        else:
            print(f"   ❓ Unexpected result: {json.dumps(result, indent=2)}")
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_bedrock_query_generation())