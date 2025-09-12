import requests
import json
import urllib.parse

# Your comprehensive healthcare schema
healthcare_schema = {
    "status": "success",
    "message": "Retrieved PostgreSQL schema: 44 tables/views from connection string",
    "database_type": "PostgreSQL",
    "database_name": "neondb",
    "tables": [
        {
            "name": "patients",
            "type": "table",
            "fields": [
                {"name": "patient_id", "type": "uuid", "nullable": False, "default": "uuid_generate_v4()"},
                {"name": "mrn", "type": "character varying(50)", "nullable": True, "default": None},
                {"name": "first_name", "type": "character varying(128)", "nullable": True, "default": None},
                {"name": "last_name", "type": "character varying(128)", "nullable": True, "default": None},
                {"name": "date_of_birth", "type": "date", "nullable": True, "default": None},
                {"name": "gender", "type": "character varying(20)", "nullable": True, "default": None},
                {"name": "blood_type", "type": "character varying(10)", "nullable": True, "default": None}
            ]
        },
        {
            "name": "encounters",
            "type": "table", 
            "fields": [
                {"name": "encounter_id", "type": "uuid", "nullable": False, "default": "uuid_generate_v4()"},
                {"name": "patient_id", "type": "uuid", "nullable": True, "default": None},
                {"name": "encounter_type", "type": "character varying(100)", "nullable": True, "default": None},
                {"name": "admission_datetime", "type": "timestamp without time zone", "nullable": True, "default": None},
                {"name": "discharge_datetime", "type": "timestamp without time zone", "nullable": True, "default": None}
            ]
        },
        {
            "name": "diagnoses",
            "type": "table",
            "fields": [
                {"name": "diagnosis_id", "type": "uuid", "nullable": False, "default": "uuid_generate_v4()"},
                {"name": "patient_id", "type": "uuid", "nullable": True, "default": None},
                {"name": "diagnosis_code", "type": "character varying(20)", "nullable": True, "default": None},
                {"name": "diagnosis_description", "type": "character varying(500)", "nullable": True, "default": None}
            ]
        }
    ]
}

# Test patient ID
patient_id = "687b0aca-ca63-4926-800b-90d5e92e5a0a"

def test_endpoint(endpoint, params):
    """Test an API endpoint with given parameters."""
    try:
        url = f"http://localhost:8000/api/v1/{endpoint}"
        print(f"\n🔍 Testing: {endpoint}")
        print(f"URL: {url}")
        print(f"Params: {list(params.keys())}")
        
        response = requests.get(url, params=params, timeout=60)
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            if 'generated_query' in result:
                print(f"Generated Query: {result['generated_query'][:200]}...")
            else:
                print(f"Response: {json.dumps(result, indent=2)[:500]}...")
        else:
            print(f"❌ Error: {response.text[:500]}...")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    print("🏥 Testing Healthcare Query Generator Endpoints")
    
    # Convert schema to JSON string
    schema_json = json.dumps(healthcare_schema)
    
    # Test basic server connectivity
    try:
        response = requests.get("http://localhost:8000/", timeout=10)
        print(f"✅ Server is running! Status: {response.status_code}")
    except:
        print("❌ Server is not responding!")
        exit(1)
    
    # Test 1: New healthcare comprehensive query
    test_endpoint("healthcare/generate-query", {
        "schema": schema_json,
        "patient_id": patient_id,
        "query_type": "comprehensive"
    })
    
    # Test 2: Clinical query
    test_endpoint("healthcare/generate-clinical", {
        "schema": schema_json,
        "patient_id": patient_id
    })
    
    # Test 3: Schema analysis
    test_endpoint("healthcare/schema-analysis", {
        "schema": schema_json
    })
    
    # Test 4: Original query generator for comparison
    test_endpoint("generate-query", {
        "schema": schema_json,
        "patient_id": patient_id
    })
    
    print("\n🎉 Testing completed!")
