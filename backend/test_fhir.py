#!/usr/bin/env python3
"""
Simple FHIR Endpoint Tester
Tests all FHIR endpoints with proper Epic OAuth flow
"""

import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:8000"
EPIC_BASE_URL = "https://fhir.epic.com/interconnect-fhir-oauth"
CLIENT_ID = "57ec0583-7f79-41e0-850f-d7c9c7282178"
CLIENT_SECRET = "RpTzlJYFjt0EW7KoSjODsDjWZu0/Q56bYPNWzqOTR/ipMD7UJWNAX5nkyCtdNIfDMFJ56c0Cp0AebIPGpRRc7A=="

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def get_epic_token():
    """Get access token from Epic"""
    print("\nGetting Epic access token...")
    
    token_url = f"{EPIC_BASE_URL}/oauth2/token"
    
    data = {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'scope': 'system/Patient.read system/Observation.read system/Condition.read'
    }
    
    try:
        response = requests.post(token_url, data=data)
        if response.status_code == 200:
            token_data = response.json()
            print("✓ Got Epic access token")
            return token_data.get('access_token')
        else:
            print(f"✗ Failed to get token: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"✗ Token request failed: {e}")
        return None

def test_fhir_endpoints():
    """Test all FHIR endpoints"""
    
    # First check if server is running
    if not test_health():
        print("Server is not running. Please start the server first.")
        return
    
    # Get Epic token
    token = get_epic_token()
    if not token:
        print("Cannot proceed without Epic token")
        return
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Test endpoints
    endpoints = [
        ("GET", "/api/v1/fhir/Patient", "Get all patients"),
        ("GET", "/api/v1/fhir/Patient/eq081-VQEgP8drUUqCWzHfw3", "Get specific patient"),
        ("GET", "/api/v1/fhir/Observation", "Get all observations"),
        ("GET", "/api/v1/fhir/Condition", "Get all conditions"),
        ("GET", "/api/v1/fhir/connections", "Get FHIR connections"),
    ]
    
    print(f"\nTesting {len(endpoints)} FHIR endpoints...\n")
    
    for method, endpoint, description in endpoints:
        print(f"Testing: {description}")
        print(f"URL: {BASE_URL}{endpoint}")
        
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=10)
            else:
                response = requests.request(method, f"{BASE_URL}{endpoint}", headers=headers, timeout=10)
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, dict):
                        print(f"Response keys: {list(data.keys())}")
                    elif isinstance(data, list):
                        print(f"Response: List with {len(data)} items")
                    print("✓ Success")
                except:
                    print(f"Response: {response.text[:200]}...")
            else:
                print(f"Error: {response.text[:200]}")
            
        except Exception as e:
            print(f"✗ Request failed: {e}")
        
        print("-" * 50)

if __name__ == "__main__":
    print("FHIR Endpoint Tester")
    print("===================")
    test_fhir_endpoints()
