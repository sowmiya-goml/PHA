#!/usr/bin/env python3
"""Test the fixed dashboard endpoint using requests."""

import requests
import json
import time

# Wait for server to be ready
print("Waiting for server to be ready...")
time.sleep(8)

try:
    # Test the dashboard endpoint
    url = "http://localhost:8000/api/v1/dashboard/patients/687b0aca-ca63-4926-800b-90d5e92e5a0a/heart-rate"
    params = {"connection_id": "68c8ea1dcee430be497cee25"}
    
    print(f"Testing endpoint: {url}")
    print(f"With parameters: {params}")
    
    response = requests.get(url, params=params, timeout=30)
    
    print(f"\nResponse Status: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print("\n✅ SUCCESS! Dashboard endpoint is working!")
            print(f"Response Data: {json.dumps(data, indent=2)}")
        except:
            print(f"Response Text: {response.text}")
    else:
        print(f"\n❌ Error {response.status_code}")
        try:
            error_data = response.json()
            print(f"Error Details: {json.dumps(error_data, indent=2)}")
        except:
            print(f"Error Text: {response.text}")
            
except requests.exceptions.RequestException as e:
    print(f"❌ Request failed: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")