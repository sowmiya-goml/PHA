#!/usr/bin/env python3
"""Test direct HTTP call to the real server with requests."""

import requests
import json

try:
    # Try the test endpoint first
    response = requests.get("http://localhost:8000/api/v1/connections", timeout=5)
    print("Status Code:", response.status_code)
    print("Response:", response.text[:200])
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")

# Test the dashboard endpoint
try:
    url = "http://localhost:8000/api/v1/dashboard/patients/687b0aca-ca63-4926-800b-90d5e92e5a0a/heart-rate"
    params = {"connection_id": "68c8ea1dcee430be497cee25"}
    response = requests.get(url, params=params, timeout=10)
    print("Dashboard Status Code:", response.status_code)
    print("Dashboard Response:", response.text[:500])
except requests.exceptions.RequestException as e:
    print(f"Dashboard request failed: {e}")