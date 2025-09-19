"""Test script for patient dashboard endpoints."""

import requests
import json
import sys
from datetime import datetime


class DashboardEndpointTester:
    """Test all dashboard endpoints with different patient IDs."""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.test_patient_ids = [
            "P12345",
            "patient-001",
            "687b0aca-ca63-4926-800b-90d5e92e5a0a",
            "test-patient-123"
        ]
        
    def test_endpoint(self, endpoint, patient_id, expected_keys=None):
        """Test a single endpoint with a patient ID."""
        url = f"{self.base_url}/api/v1/dashboard/{endpoint.format(patient_id=patient_id)}"
        
        try:
            print(f"🔍 Testing: {url}")
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success: {response.status_code}")
                
                # Check for expected keys
                if expected_keys:
                    for key in expected_keys:
                        if key in data:
                            print(f"   ✓ Has '{key}': {data[key]}")
                        else:
                            print(f"   ❌ Missing '{key}'")
                
                # Show data source
                if 'data_source' in data:
                    print(f"   📊 Data source: {data['data_source']}")
                
                print(f"   📄 Response: {json.dumps(data, indent=2)[:200]}...")
                return True
                
            else:
                print(f"❌ Failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"🔌 Connection error: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
    
    def test_health_endpoint(self):
        """Test the health check endpoint to see database status."""
        print(f"\n🏥 Testing Health Check")
        print("=" * 60)
        
        url = f"{self.base_url}/health"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check successful")
                print(f"📊 Databases status:")
                if 'databases' in data:
                    for db_name, status in data['databases'].items():
                        print(f"   - {db_name}: {status}")
                print(f"📄 Full response: {json.dumps(data, indent=2)}")
            else:
                print(f"❌ Health check failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Health check error: {e}")
    
    def test_all_endpoints(self):
        """Test all dashboard endpoints."""
        print(f"🧪 Testing Patient Dashboard Endpoints")
        print(f"🌐 Base URL: {self.base_url}")
        print(f"📅 Test Time: {datetime.now().isoformat()}")
        print("=" * 80)
        
        # Test health first
        self.test_health_endpoint()
        
        endpoints = [
            {
                "name": "Heart Rate",
                "endpoint": "patients/{patient_id}/heart-rate",
                "expected_keys": ["heart_rate", "status", "timestamp", "patient_id"]
            },
            {
                "name": "Blood Pressure", 
                "endpoint": "patients/{patient_id}/blood-pressure",
                "expected_keys": ["systolic", "diastolic", "status", "timestamp", "patient_id"]
            },
            {
                "name": "BMI",
                "endpoint": "patients/{patient_id}/bmi", 
                "expected_keys": ["bmi", "trend", "timestamp", "patient_id"]
            },
            {
                "name": "SpO2",
                "endpoint": "patients/{patient_id}/spo2",
                "expected_keys": ["spo2_percentage", "status", "timestamp", "patient_id"]
            },
            {
                "name": "Temperature",
                "endpoint": "patients/{patient_id}/temperature",
                "expected_keys": ["temperature_celsius", "temperature_fahrenheit", "status", "timestamp", "patient_id"]
            },
            {
                "name": "Blood Sugar",
                "endpoint": "patients/{patient_id}/blood-sugar",
                "expected_keys": ["glucose_level", "trend", "timestamp", "patient_id"]
            },
            {
                "name": "Recovery Tracker",
                "endpoint": "patients/{patient_id}/recovery-tracker",
                "expected_keys": ["patient_id", "recovery_data", "current_stage", "timestamp"]
            }
        ]
        
        total_tests = 0
        successful_tests = 0
        
        for patient_id in self.test_patient_ids:
            print(f"\n👤 Testing Patient ID: {patient_id}")
            print("-" * 60)
            
            for endpoint_info in endpoints:
                print(f"\n🔬 {endpoint_info['name']}")
                success = self.test_endpoint(
                    endpoint_info['endpoint'],
                    patient_id,
                    endpoint_info['expected_keys']
                )
                total_tests += 1
                if success:
                    successful_tests += 1
                print()
        
        # Test error cases
        print(f"\n🚨 Testing Error Cases")
        print("-" * 60)
        
        # Test with invalid patient ID
        print(f"\n🔬 Invalid Patient ID (empty)")
        self.test_endpoint("patients/{patient_id}/heart-rate", "")
        total_tests += 1
        
        print(f"\n🔬 Invalid Patient ID (too long)")
        self.test_endpoint("patients/{patient_id}/heart-rate", "a" * 100)
        total_tests += 1
        
        # Summary
        print(f"\n📊 Test Summary")
        print("=" * 60)
        print(f"Total tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Failed: {total_tests - successful_tests}")
        print(f"Success rate: {(successful_tests/total_tests)*100:.1f}%")
        
        if successful_tests == total_tests:
            print("🎉 All tests passed!")
            return True
        else:
            print(f"⚠️  {total_tests - successful_tests} tests failed")
            return False


def test_swagger_ui():
    """Test if Swagger UI is accessible."""
    print(f"\n📚 Testing Swagger UI")
    print("-" * 60)
    
    try:
        response = requests.get("http://localhost:8000/docs", timeout=5)
        if response.status_code == 200:
            print("✅ Swagger UI accessible at http://localhost:8000/docs")
            print("💡 You can test endpoints interactively there")
        else:
            print(f"❌ Swagger UI not accessible: {response.status_code}")
    except Exception as e:
        print(f"🔌 Cannot reach Swagger UI: {e}")


def main():
    """Main test function."""
    print("🏥 Patient Dashboard API Test Suite")
    print("=" * 80)
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server not responding properly")
            print("💡 Make sure the server is running: python scripts/start.py")
            sys.exit(1)
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to server at http://localhost:8000")
        print("💡 Make sure the server is running: python scripts/start.py")
        sys.exit(1)
    
    # Run tests
    tester = DashboardEndpointTester()
    success = tester.test_all_endpoints()
    
    # Test Swagger UI
    test_swagger_ui()
    
    # Final status
    print(f"\n🏁 Test Complete")
    if success:
        print("✅ All dashboard endpoints are working correctly!")
        print("📊 The system gracefully falls back to mock data when database is unavailable")
    else:
        print("⚠️  Some endpoints had issues - check the logs above")
    
    print(f"\n🔗 Useful Links:")
    print(f"   - API Documentation: http://localhost:8000/docs")
    print(f"   - Health Check: http://localhost:8000/health")
    print(f"   - Example Heart Rate: http://localhost:8000/api/v1/dashboard/patients/P12345/heart-rate")


if __name__ == "__main__":
    main()