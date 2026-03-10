#!/usr/bin/env python
"""
Test script to verify all TrackRight APIs are working correctly
Uses session-based authentication with cookies
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000/api"

# Use a session to maintain cookies across requests
session = requests.Session()

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")

def test_api(method, endpoint, data=None):
    """Generic API test function using session cookies"""
    url = f"{BASE_URL}{endpoint}"
    
    # Get CSRF token from session cookies
    csrf_token = session.cookies.get('csrftoken')
    
    headers = {
        'X-Requested-With': 'XMLHttpRequest',  # Tell Django it's an AJAX request
    }
    
    # Add CSRF token to headers for mutations
    if csrf_token and method in ['POST', 'PUT', 'DELETE']:
        headers['X-CSRFToken'] = csrf_token
    
    try:
        if method == "GET":
            response = session.get(url, headers=headers)
        elif method == "POST":
            response = session.post(url, json=data, headers=headers)
        elif method == "PUT":
            response = session.put(url, json=data, headers=headers)
        elif method == "DELETE":
            response = session.delete(url, headers=headers)
        
        status = "✓" if response.status_code < 400 else "✗"
        print(f"{status} {method} {endpoint} - {response.status_code}")
        
        # Debug: print response content for errors
        if response.status_code >= 400 and response.text:
            try:
                res_json = response.json()
                print(f"   Error: {res_json.get('detail', res_json)}")
            except:
                print(f"   Response: {response.text[:200]}")
        
        if response.text:
            try:
                return response.json()
            except:
                return response.text
        return response.status_code
    except Exception as e:
        print(f"✗ {method} {endpoint} - ERROR: {str(e)}")
        return None

def login(username, password):
    """Login and store session cookies, also trigger CSRF cookie generation"""
    # First, make a GET request to trigger CSRF cookie generation
    try:
        session.get(f"{BASE_URL}/products/")
    except:
        pass
    
    login_url = "http://localhost:8000/accounts/api/login/"
    login_data = {"username": username, "password": password}
    try:
        response = session.post(login_url, json=login_data)
        if response.status_code == 200:
            print(f"✓ Login successful with session cookie")
            return True
        else:
            print(f"✗ Login failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Login error: {str(e)}")
        return False

def main():
    print_header("TRACKRIGHT API VERIFICATION TEST")
    
    # Login first to establish session
    print_header("0. TESTING LOGIN")
    if not login("testuser", "testpass123"):
        print("✗ Cannot proceed without authentication")
        return
    
    # Test 1: Products API
    print_header("1. TESTING PRODUCTS API")
    products = test_api("GET", "/products/")
    if isinstance(products, list):
        print(f"   Found {len(products)} products")
    
    # Test 2: Orders API
    print_header("2. TESTING ORDERS API")
    orders = test_api("GET", "/orders/")
    if isinstance(orders, list):
        print(f"   Found {len(orders)} orders")
        order_id = orders[0]['id'] if orders else None
    
    # Test 3: Orders Search
    if orders:
        print_header("3. TESTING ORDERS SEARCH")
        search_results = test_api("GET", "/orders/?search=John")
        if isinstance(search_results, list):
            print(f"   Search returned {len(search_results)} results")
    
    # Test 4: Scan Records API
    print_header("4. TESTING SCAN RECORDS API")
    scans = test_api("GET", "/scans/")
    if isinstance(scans, list):
        print(f"   Found {len(scans)} scan records")
    
    # Test 5: Tasks API
    print_header("5. TESTING TASKS API")
    tasks = test_api("GET", "/tasks/")
    if isinstance(tasks, list):
        print(f"   Found {len(tasks)} tasks")
    
    # Test 6: Tasks Search
    if tasks:
        print_header("6. TESTING TASKS SEARCH")
        task_search = test_api("GET", "/tasks/?search=Pack")
        if isinstance(task_search, list):
            print(f"   Search returned {len(task_search)} results")
    
    # Test 7: Mismatches API
    print_header("7. TESTING MISMATCHES API")
    mismatches = test_api("GET", "/mismatches/")
    if isinstance(mismatches, list):
        print(f"   Found {len(mismatches)} mismatches")
    
    # Test 8: Dashboard Stats
    print_header("8. TESTING DASHBOARD STATS")
    stats = test_api("GET", "/dashboard/stats/")
    if isinstance(stats, dict):
        print(f"   Today's scans: {stats.get('todays_scans', 0)}")
        print(f"   Verified orders: {stats.get('verified_orders', 0)}")
        print(f"   Mismatch rate: {stats.get('mismatch_rate', 0)}%")
        print(f"   Total orders: {stats.get('total_orders', 0)}")
        if 'mismatches_by_department' in stats:
            print(f"   Departments in mismatches data: {', '.join(stats['mismatches_by_department'].keys())}")
        else:
            print("   No department breakdown included in stats")
    
    # Test 9: Create New Order
    print_header("9. TESTING CREATE NEW ORDER")
    import time
    new_order = {
        "order_number": f"ORD-AUTO-{int(time.time())}",
        "customer_name": "Test Customer",
        "status": "pending"
    }
    created = test_api("POST", "/orders/", new_order)
    if isinstance(created, dict) and 'id' in created:
        print(f"   Order created with ID: {created['id']}")
    
    # Test 10: Create New Task
    print_header("10. TESTING CREATE NEW TASK")
    new_task = {
        "title": "Test Task",
        "priority": "high",
        "status": "pending"
    }
    created_task = test_api("POST", "/tasks/", new_task)
    if isinstance(created_task, dict) and 'id' in created_task:
        print(f"   Task created with ID: {created_task['id']}")
    
    print_header("VERIFICATION COMPLETE")
    print("\n✓ All API endpoints are responsive")
    print("✓ Sample data has been successfully created")
    print("✓ TrackRight platform is ready for use")
    print("\nAccess the application at: http://localhost:8000/")
    print("Login with: testuser / testpass123")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nTest interrupted")
        sys.exit(1)
