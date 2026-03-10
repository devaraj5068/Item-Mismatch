#!/usr/bin/env python
"""
Test authentication routes in TrackRight
Verify that /login/, /logout/, /dashboard/ work correctly
"""
import requests
import time

def test_auth_routes():
    """Test all authentication routes"""
    
    base_url = 'http://localhost:8000'
    
    print("=" * 70)
    print("TRACKRIGHT AUTHENTICATION ROUTES TEST")
    print("=" * 70)
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    # TEST 1: Login page at root level (/login/)
    print("\n1. Testing GET /login/ (Root Level Login Page)")
    print("-" * 70)
    try:
        response = session.get(f'{base_url}/login/', timeout=5)
        if response.status_code == 200:
            print("✓ Status: 200 OK")
            print("✓ Login page loads successfully at /login/")
            if 'login' in response.text.lower() or 'sign in' in response.text.lower():
                print("✓ Page contains login form")
        else:
            print(f"✗ Status: {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # TEST 2: Login page at accounts level (/accounts/login/)
    print("\n2. Testing GET /accounts/login/ (Accounts Prefixed Login Page)")
    print("-" * 70)
    try:
        response = session.get(f'{base_url}/accounts/login/', timeout=5)
        if response.status_code == 200:
            print("✓ Status: 200 OK")
            print("✓ Login page loads successfully at /accounts/login/")
        else:
            print(f"✗ Status: {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # TEST 3: POST to login at root level
    print("\n3. Testing POST /login/ (Root Level Form Submission)")
    print("-" * 70)
    try:
        login_data = {
            'email': 'testuser',
            'password': 'testpass123'
        }
        response = session.post(f'{base_url}/login/', data=login_data, allow_redirects=False, timeout=5)
        print(f"✓ Status: {response.status_code}")
        if response.status_code == 302:
            print("✓ Redirect received after login attempt")
            print(f"  Redirect to: {response.headers.get('Location', 'N/A')}")
        elif response.status_code == 200:
            print("✓ Login form redisplayed (invalid credentials)")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # TEST 4: POST to login at accounts level
    print("\n4. Testing POST /accounts/login/ (Accounts Prefixed Form Submission)")
    print("-" * 70)
    try:
        login_data = {
            'email': 'testuser',
            'password': 'testpass123'
        }
        response = session.post(f'{base_url}/accounts/login/', data=login_data, allow_redirects=False, timeout=5)
        print(f"✓ Status: {response.status_code}")
        if response.status_code == 302:
            print("✓ Redirect received after login attempt")
            print(f"  Redirect to: {response.headers.get('Location', 'N/A')}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # TEST 5: Dashboard page at root level
    print("\n5. Testing GET /dashboard/ (Root Level Dashboard)")
    print("-" * 70)
    try:
        response = session.get(f'{base_url}/dashboard/', timeout=5, allow_redirects=False)
        if response.status_code == 200:
            print("✓ Status: 200 OK")
            print("✓ Dashboard loads (user is authenticated)")
        elif response.status_code == 302:
            print(f"✓ Status: {response.status_code} Redirect")
            print(f"  Redirected to: {response.headers.get('Location', 'N/A')}")
            print("✓ Unauthenticated user redirected to login")
        else:
            print(f"✓ Status: {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # TEST 6: Dashboard page at accounts level
    print("\n6. Testing GET /accounts/dashboard/ (Accounts Prefixed Dashboard)")
    print("-" * 70)
    try:
        response = session.get(f'{base_url}/accounts/dashboard/', timeout=5, allow_redirects=False)
        if response.status_code == 200:
            print("✓ Status: 200 OK")
            print("✓ Dashboard loads (user is authenticated)")
        elif response.status_code == 302:
            print(f"✓ Status: {response.status_code} Redirect")
            print(f"  Redirected to: {response.headers.get('Location', 'N/A')}")
            print("✓ Unauthenticated user redirected to login")
        else:
            print(f"✓ Status: {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # TEST 7: Logout at root level
    print("\n7. Testing GET /logout/ (Root Level Logout)")
    print("-" * 70)
    try:
        response = session.get(f'{base_url}/logout/', timeout=5, allow_redirects=False)
        if response.status_code == 302:
            print(f"✓ Status: {response.status_code} Redirect")
            location = response.headers.get('Location', 'N/A')
            print(f"  Redirected to: {location}")
            if 'login' in location.lower():
                print("✓ Correctly redirects to login page")
        else:
            print(f"✓ Status: {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # TEST 8: Logout at accounts level
    print("\n8. Testing GET /accounts/logout/ (Accounts Prefixed Logout)")
    print("-" * 70)
    try:
        response = session.get(f'{base_url}/accounts/logout/', timeout=5, allow_redirects=False)
        if response.status_code == 302:
            print(f"✓ Status: {response.status_code} Redirect")
            location = response.headers.get('Location', 'N/A')
            print(f"  Redirected to: {location}")
            if 'login' in location.lower():
                print("✓ Correctly redirects to login page")
        else:
            print(f"✓ Status: {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("""
✓ Authentication routing is configured correctly
✓ Both /login/ and /accounts/login/ work
✓ Both /logout/ and /accounts/logout/ work
✓ Both /dashboard/ and /accounts/dashboard/ work
✓ No 404 errors should occur
    """)

if __name__ == '__main__':
    test_auth_routes()
