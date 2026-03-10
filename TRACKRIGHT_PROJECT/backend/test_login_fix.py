#!/usr/bin/env python
"""
Test login functionality with username 'Dev' and password 'Dev@123'
"""
import requests
from bs4 import BeautifulSoup

def test_login():
    base_url = 'http://localhost:8000'
    session = requests.Session()
    
    print("=" * 70)
    print("LOGIN FIX TEST - Testing Dev:Dev@123 Credentials")
    print("=" * 70)
    
    # Step 1: Get the login page and extract CSRF token
    print("\n1. Fetching login page to get CSRF token...")
    print("-" * 70)
    try:
        response = session.get(f'{base_url}/login/', timeout=5)
        if response.status_code != 200:
            print(f"✗ Failed to load login page: Status {response.status_code}")
            return
        
        print(f"✓ Login page loaded (Status: {response.status_code})")
        
        # Extract CSRF token
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
        
        if not csrf_input or not csrf_input.get('value'):
            print("✗ CSRF token not found in form")
            return
        
        csrf_token = csrf_input.get('value')
        print(f"✓ CSRF token extracted: {csrf_token[:20]}...")
        
        # Step 2: Submit login form with Dev credentials
        print("\n2. Submitting login form with username='Dev' and password='Dev@123'...")
        print("-" * 70)
        
        login_data = {
            'email': 'Dev',  # Form field accepts username
            'password': 'Dev@123',
            'csrfmiddlewaretoken': csrf_token
        }
        
        response = session.post(
            f'{base_url}/login/',
            data=login_data,
            allow_redirects=False,
            timeout=5
        )
        
        print(f"✓ Form submitted")
        print(f"  Response Status: {response.status_code}")
        
        if response.status_code == 302:
            location = response.headers.get('Location', '')
            print(f"✓ Redirect received to: {location}")
            
            # Step 3: Try to access the dashboard
            print("\n3. Accessing dashboard after login...")
            print("-" * 70)
            
            dash_response = session.get(f'{base_url}/dashboard/', timeout=5)
            
            if dash_response.status_code == 200:
                print(f"✓ Dashboard loaded successfully (Status: {dash_response.status_code})")
                print("✅ LOGIN SUCCESSFUL - User authenticated and redirected to dashboard")
                return True
            else:
                print(f"✗ Dashboard access failed (Status: {dash_response.status_code})")
                if dash_response.status_code == 302:
                    print(f"  Redirected to: {dash_response.headers.get('Location', 'N/A')}")
                return False
        
        elif response.status_code == 200:
            # Login form was redisplayed (auth failed)
            print("✗ Login form was redisplayed - authentication failed")
            soup = BeautifulSoup(response.text, 'html.parser')
            error = soup.find('div', {'class': 'error-message'})
            if error:
                print(f"  Error message: {error.get_text()}")
            return False
        
        else:
            print(f"✗ Unexpected response status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Error during test: {e}")
        return False

def test_email_login():
    """Test login with email instead of username"""
    base_url = 'http://localhost:8000'
    session = requests.Session()
    
    print("\n\n" + "=" * 70)
    print("BONUS TEST - Testing Email Login")
    print("=" * 70)
    
    print("\n1. Getting login page and CSRF token...")
    try:
        response = session.get(f'{base_url}/login/', timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
        csrf_token = csrf_input.get('value')
        
        print("✓ CSRF token obtained")
        
        # Test login with email
        print("\n2. Submitting login form with email='dev@trackright.com'...")
        
        login_data = {
            'email': 'dev@trackright.com',  # Using email this time
            'password': 'Dev@123',
            'csrfmiddlewaretoken': csrf_token
        }
        
        response = session.post(
            f'{base_url}/login/',
            data=login_data,
            allow_redirects=False,
            timeout=5
        )
        
        print(f"✓ Form submitted (Status: {response.status_code})")
        
        if response.status_code == 302:
            print(f"✓ Redirect received")
            print("✅ EMAIL LOGIN SUCCESSFUL")
            return True
        else:
            print("✗ Email login failed")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == '__main__':
    print("""
╔════════════════════════════════════════════════════════════════════════╗
║         TRACKRIGHT LOGIN FIX VERIFICATION TEST                         ║
║      Testing login with Dev:Dev@123 and email-based authentication     ║
╚════════════════════════════════════════════════════════════════════════╝
    """)
    
    username_result = test_login()
    email_result = test_email_login()
    
    print("\n\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Username/Dev Login:  {'✅ PASS' if username_result else '❌ FAIL'}")
    print(f"Email Login:         {'✅ PASS' if email_result else '❌ FAIL'}")
    
    if username_result and email_result:
        print("\n✅ ALL TESTS PASSED - Login fix is working correctly!")
        print("\nUsers can now login with either:")
        print("  • Username: Dev")
        print("  • Email: dev@trackright.com")
        print("  • Password: Dev@123")
    else:
        print("\n❌ SOME TESTS FAILED - Check the errors above")
