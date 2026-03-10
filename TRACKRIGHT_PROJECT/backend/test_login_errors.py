#!/usr/bin/env python
import requests
import json

print("Testing Login Endpoint - Wrong Credentials")
print("=" * 50)

url = "http://localhost:8000/api/login/"

# Test with correct credentials
print("Testing CORRECT credentials:")
data = {"username": "Dev", "password": "Dev@123"}
response = requests.post(url, json=data)
print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")

print("\nTesting WRONG credentials:")
data = {"username": "Dev", "password": "wrongpassword"}
response = requests.post(url, json=data)
print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")

print("\nTesting NON-EXISTENT user:")
data = {"username": "nonexistent", "password": "password"}
response = requests.post(url, json=data)
print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")

print("=" * 50)
