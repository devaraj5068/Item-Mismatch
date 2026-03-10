#!/usr/bin/env python
import requests
import json

print("Testing Login Endpoint")
print("=" * 50)

url = "http://localhost:8000/api/login/"
data = {"email": "Dev", "password": "Dev@123"}

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        print("\n✓ LOGIN SUCCESSFUL!")
        token = response.json().get('token')
        print(f"Token: {token}")
    else:
        print("\n✗ LOGIN FAILED")
except Exception as e:
    print(f"Error: {e}")

print("=" * 50)
