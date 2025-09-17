"""Test the enhanced Snowflake connection with different account formats."""

import asyncio
import requests
import json


async def test_snowflake_connection_variants():
    """Test Snowflake connection with different account identifier formats."""
    
    print("🧪 Testing Enhanced Snowflake Connection Support")
    print("=" * 60)
    
    # Test data with different connection string formats
    test_connections = [
        {
            "name": "Snowflake - Account Only",
            "connection_data": {
                "name": "Snowflake Test 1 - Account Only",
                "database_type": "snowflake",
                "connection_string": "snowflake://sowmiya:Sowmiya22112004@qgkxkwg-mr95865/pha/my_schema?warehouse=COMPUTE_WH&role=SYSADMIN"
            }
        },
        {
            "name": "Snowflake - With Region",
            "connection_data": {
                "name": "Snowflake Test 2 - With Region",
                "database_type": "snowflake", 
                "connection_string": "snowflake://sowmiya:Sowmiya22112004@qgkxkwg-mr95865.ap-south-1.aws/pha/my_schema?warehouse=COMPUTE_WH&role=SYSADMIN"
            }
        },
        {
            "name": "Snowflake - Full Hostname",
            "connection_data": {
                "name": "Snowflake Test 3 - Full Hostname",
                "database_type": "snowflake",
                "connection_string": "snowflake://sowmiya:Sowmiya22112004@qgkxkwg-mr95865.ap-south-1.aws.snowflakecomputing.com/pha/my_schema?warehouse=COMPUTE_WH&role=SYSADMIN"
            }
        }
    ]
    
    base_url = "http://localhost:8000/api/v1"
    
    # Test each connection variant
    for i, test_case in enumerate(test_connections, 1):
        print(f"\n{i}. Testing {test_case['name']}")
        print("-" * 40)
        
        try:
            # Create connection
            print("📝 Creating connection...")
            create_response = requests.post(
                f"{base_url}/connections",
                json=test_case["connection_data"],
                timeout=30
            )
            
            if create_response.status_code == 200:
                connection_data = create_response.json()
                connection_id = connection_data.get("id")
                print(f"✅ Connection created with ID: {connection_id}")
                
                # Test the connection
                print("🔌 Testing connection...")
                test_response = requests.post(
                    f"{base_url}/connections/{connection_id}/test",
                    timeout=60
                )
                
                if test_response.status_code == 200:
                    test_result = test_response.json()
                    print(f"📊 Test Result:")
                    print(f"   Status: {test_result.get('status')}")
                    print(f"   Message: {test_result.get('message')}")
                    
                    if test_result.get('status') == 'success':
                        print("🎉 Connection test successful!")
                        
                        # Try schema extraction if connection works
                        print("📚 Testing schema extraction...")
                        schema_response = requests.get(
                            f"{base_url}/connections/{connection_id}/schema",
                            timeout=60
                        )
                        
                        if schema_response.status_code == 200:
                            schema_result = schema_response.json()
                            print(f"📋 Schema extraction result:")
                            print(f"   Status: {schema_result.get('status')}")
                            if schema_result.get('status') == 'success':
                                tables = schema_result.get('data', {}).get('tables', [])
                                print(f"   Found {len(tables)} tables")
                            else:
                                print(f"   Error: {schema_result.get('message')}")
                        else:
                            print(f"❌ Schema extraction failed: {schema_response.status_code}")
                            
                    else:
                        print(f"⚠️ Connection test failed: {test_result.get('message')}")
                        
                else:
                    print(f"❌ Connection test request failed: {test_response.status_code}")
                    try:
                        error_data = test_response.json()
                        print(f"   Error: {error_data}")
                    except:
                        print(f"   Error: {test_response.text}")
                
                # Clean up - delete the test connection
                print("🧹 Cleaning up...")
                delete_response = requests.delete(f"{base_url}/connections/{connection_id}")
                if delete_response.status_code == 200:
                    print("✅ Test connection deleted")
                else:
                    print(f"⚠️ Failed to delete test connection: {delete_response.status_code}")
                    
            else:
                print(f"❌ Connection creation failed: {create_response.status_code}")
                try:
                    error_data = create_response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {create_response.text}")
                    
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to API server. Make sure it's running on http://localhost:8000")
            break
        except requests.exceptions.Timeout:
            print("⏰ Request timed out")
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🏁 Test completed!")
    print("\n💡 Key Points:")
    print("- The enhanced connection method tries multiple account formats")
    print("- If the first format fails, it automatically tries alternatives")
    print("- Error messages now include debugging information")
    print("- Check the detailed error messages for troubleshooting hints")


if __name__ == "__main__":
    asyncio.run(test_snowflake_connection_variants())