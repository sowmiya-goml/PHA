"""Test the specific API endpoint that handles healthcare query generation."""

import requests
import json


def test_healthcare_api_endpoint():
    """Test the healthcare API endpoint directly."""
    
    print("🔍 Testing Healthcare API Endpoint")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test data
    test_cases = [
        {
            "name": "Test with existing Snowflake connection",
            "endpoint": "/api/v1/healthcare/generate-query-by-connection",
            "params": {
                "connection_id": "67412db2ae5b5ec1b3ea46b1",  # Replace with actual connection ID
                "patient_id": "test-123",
                "query_type": "basic"
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🧪 {test_case['name']}")
        print(f"   Endpoint: {test_case['endpoint']}")
        print(f"   Params: {test_case['params']}")
        
        try:
            # Make the API request
            response = requests.get(
                f"{base_url}{test_case['endpoint']}",
                params=test_case['params'],
                timeout=60
            )
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("   ✅ API call successful!")
                
                # Check key fields
                if data.get('generated_query'):
                    print(f"   Generated Query: {data['generated_query'][:100]}...")
                    print(f"   Model Used: {data.get('model_used', 'N/A')}")
                    print(f"   Status: {data.get('status', 'N/A')}")
                else:
                    print("   ❌ No query generated in response")
                    print(f"   Full Response: {json.dumps(data, indent=2)}")
                    
            else:
                print(f"   ❌ API call failed")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Raw Error: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("   ❌ Connection failed - is the server running on localhost:8000?")
        except requests.exceptions.Timeout:
            print("   ❌ Request timeout - LLM might be taking too long")
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")


if __name__ == "__main__":
    test_healthcare_api_endpoint()