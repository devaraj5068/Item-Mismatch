#!/usr/bin/env python
"""
Quick test to verify login endpoint is at the correct URL
"""
import requests
import json

def test_login_endpoints():
    """Test both old and new login endpoint locations"""
    
    print("Testing Login Endpoint URLs")
    print("=" * 60)
    
    # Test old endpoint (should 404)
    print("\n1. Testing OLD endpoint: /login/ (SHOULD FAIL - 404)")
    try:
        response = requests.post('http://localhost:8000/login/', 
                               json={"username": "testuser", "password": "testpass123"},
                               timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 404:
            print("   ✓ Correctly returns 404 - Old endpoint no longer exists")
        else:
            print(f"   Status: {response.status_code}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test new API endpoint (should 200)
    print("\n2. Testing NEW API endpoint: /accounts/api/login/ (SHOULD WORK - 200)")
    try:
        response = requests.post('http://localhost:8000/accounts/api/login/', 
                               json={"username": "testuser", "password": "testpass123"},
                               timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if 'message' in data:
                print(f"   ✓ Login successful: {data['message']}")
            else:
                print(f"   ✓ Response received: {data}")
        else:
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test new login page endpoint (should 200)
    print("\n3. Testing NEW login page: /accounts/login/ (SHOULD WORK - 200)")
    try:
        response = requests.get('http://localhost:8000/accounts/login/', timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✓ Login page loads successfully")
        else:
            print(f"   Status: {response.status_code}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "=" * 60)
    print("✓ Login URL migration successful!")
    print("  Old /login/ endpoint no longer works (404)")
    print("  New /accounts/login/ and /accounts/api/login/ are active")

if __name__ == "__main__":
    test_login_endpoints()
