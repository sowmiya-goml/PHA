"""Simple server test script."""

import socket
import sys

def check_server_port():
    """Check if server is listening on port 8000."""
    try:
        # Create a socket object
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)  # 5 second timeout
        
        # Test connection to localhost:8000
        result = sock.connect_ex(('localhost', 8000))
        sock.close()
        
        if result == 0:
            print("✅ Server is listening on port 8000")
            return True
        else:
            print("❌ Server is not listening on port 8000")
            return False
            
    except Exception as e:
        print(f"❌ Error checking server: {e}")
        return False

def test_simple_request():
    """Test a simple HTTP request."""
    try:
        import requests
        
        print("🔍 Testing health endpoint...")
        response = requests.get("http://localhost:8000/health", timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:500]}...")
        
        if response.status_code == 200:
            print("✅ Health endpoint is working!")
            return True
        else:
            print("❌ Health endpoint returned error")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server")
        return False
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def test_dashboard_endpoint():
    """Test a dashboard endpoint."""
    try:
        import requests
        
        url = "http://localhost:8000/api/v1/dashboard/patients/P12345/heart-rate"
        print(f"🔍 Testing dashboard endpoint: {url}")
        
        response = requests.get(url, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:500]}...")
        
        if response.status_code == 200:
            print("✅ Dashboard endpoint is working!")
            return True
        else:
            print("❌ Dashboard endpoint returned error")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server")
        return False
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 Testing PHA Server")
    print("=" * 40)
    
    # Check if port is open
    if not check_server_port():
        print("💡 Make sure to start the server: python scripts/start.py")
        sys.exit(1)
    
    # Test health endpoint
    print("\n📋 Testing Health Endpoint")
    if not test_simple_request():
        print("⚠️  Health endpoint failed")
    
    # Test dashboard endpoint
    print("\n📊 Testing Dashboard Endpoint")
    if not test_dashboard_endpoint():
        print("⚠️  Dashboard endpoint failed")
    
    print("\n✅ Test complete!")

if __name__ == "__main__":
    main()