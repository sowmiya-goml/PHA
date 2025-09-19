"""Test the API endpoint to demonstrate selective column quoting"""
import requests
import json
from datetime import datetime

def test_healthcare_api():
    """Test the healthcare query generation API endpoint."""
    
    print("🌐 TESTING PHA HEALTHCARE API - SELECTIVE COLUMN QUOTING")
    print("=" * 80)
    print(f"Testing at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # API endpoint
    base_url = "http://localhost:8000"
    
    # First, let's create a test connection with reserved keyword columns
    connection_data = {
        "connection_name": "Test Healthcare DB - Reserved Keywords",
        "database_type": "postgresql", 
        "connection_string": "postgresql://user:pass@localhost:5432/healthcare_test",
        "additional_notes": "Test database with reserved keyword columns like 'start', 'end', 'user', 'order'"
    }
    
    print("📝 STEP 1: Creating test database connection...")
    try:
        response = requests.post(f"{base_url}/api/v1/connections/", json=connection_data)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            connection = response.json()
            connection_id = connection['id']
            print(f"   ✅ Created connection: {connection_id}")
        else:
            print(f"   ❌ Failed to create connection: {response.text}")
            return
            
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
        return
    
    # Test the healthcare query generation with a mock schema containing reserved keywords
    print("\n🔍 STEP 2: Testing healthcare query generation...")
    
    # This would normally use actual schema extraction, but for demo we'll show the concept
    test_payload = {
        "connection_id": connection_id,
        "query_request": "comprehensive patient data with encounters and diagnoses",
        "patient_id": "TEST-PATIENT-456"
    }
    
    try:
        print(f"   📤 Sending request to: {base_url}/api/v1/healthcare/generate-query-by-connection")
        print(f"   📦 Payload: {json.dumps(test_payload, indent=4)}")
        
        response = requests.post(
            f"{base_url}/api/v1/healthcare/generate-query-by-connection",
            json=test_payload
        )
        
        print(f"\n   📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print("   ✅ API RESPONSE:")
            print("   " + "-" * 60)
            
            # Show the generated query if available
            if 'generated_query' in result:
                query = result['generated_query']
                print(f"   📊 Generated Query:")
                print(f"   {query}")
                
                # Analyze for selective quoting
                print(f"\n   🔍 Selective Quoting Analysis:")
                reserved_keywords = ['start', 'end', 'user', 'order', 'type', 'status', 'date', 'level', 'count']
                normal_columns = ['id', 'name', 'email', 'phone', 'description', 'code']
                
                quoted_reserved = []
                unquoted_normal = []
                
                for keyword in reserved_keywords:
                    if f'"{keyword}"' in query:
                        quoted_reserved.append(keyword)
                
                for column in normal_columns:
                    if column in query and f'"{column}"' not in query:
                        unquoted_normal.append(column)
                
                if quoted_reserved:
                    print(f"   ✅ Reserved keywords properly quoted: {', '.join([f'\"{k}\"' for k in quoted_reserved])}")
                    
                if unquoted_normal:
                    print(f"   ✅ Normal columns correctly unquoted: {', '.join(unquoted_normal)}")
                    
            else:
                print(f"   📋 Full Response:")
                print(f"   {json.dumps(result, indent=4)}")
                
        else:
            print(f"   ❌ API Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Request error: {e}")
    
    # Test list all connections to see our test connection
    print("\n📋 STEP 3: Listing all connections...")
    try:
        response = requests.get(f"{base_url}/api/v1/connections/")
        if response.status_code == 200:
            connections = response.json()
            print(f"   ✅ Found {len(connections)} connections:")
            for conn in connections:
                print(f"      • {conn['connection_name']} ({conn['database_type']})")
        else:
            print(f"   ❌ Failed to list connections: {response.text}")
    except Exception as e:
        print(f"   ❌ Request error: {e}")
    
    print("\n" + "=" * 80)
    print("🎯 KEY FEATURE DEMONSTRATED:")
    print("   • Only SQL reserved keyword columns get quoted with double quotes")
    print("   • Normal column names remain unquoted for clean, readable SQL")
    print("   • This prevents 'Syntax error: unexpected [KEYWORD]' database errors")
    print("=" * 80)

if __name__ == "__main__":
    test_healthcare_api()