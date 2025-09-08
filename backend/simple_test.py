#!/usr/bin/env python3
"""
Simple Local API Tester - Tests only local endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_local_endpoints():
    """Test only local API endpoints"""
    
    print("Local API Endpoint Tester")
    print("========================")
    
    # Test health first
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        if response.status_code != 200:
            print("   Server is not healthy. Stopping tests.")
            return
    except Exception as e:
        print(f"   ✗ Health check failed: {e}")
        print("   Server is not running. Please start the server first.")
        return
    
    print("   ✓ Server is healthy\n")
    
    # Test local endpoints
    endpoints = [
        ("GET", "/api/v1/connections", "Get database connections"),
        ("GET", "/api/v1/connections/test", "Test database connection"),
        ("GET", "/api/v1/fhir/connections", "Get FHIR connections"),
        ("GET", "/docs", "API Documentation"),
    ]
    
    for i, (method, endpoint, description) in enumerate(endpoints, 2):
        print(f"{i}. Testing: {description}")
        print(f"   URL: {BASE_URL}{endpoint}")
        
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    if 'application/json' in response.headers.get('content-type', ''):
                        data = response.json()
                        if isinstance(data, dict):
                            print(f"   Keys: {list(data.keys())}")
                        elif isinstance(data, list):
                            print(f"   Items: {len(data)}")
                        print("   ✓ Success")
                    else:
                        print("   ✓ Success (HTML/other content)")
                except Exception as e:
                    print(f"   Response: {str(response.text)[:100]}...")
                    print("   ✓ Success")
            else:
                print(f"   ✗ Error: {response.text[:100]}")
                
        except Exception as e:
            print(f"   ✗ Request failed: {e}")
        
        print()

if __name__ == "__main__":
    test_local_endpoints()
