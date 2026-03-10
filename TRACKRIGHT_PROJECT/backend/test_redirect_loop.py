#!/usr/bin/env python
"""
Comprehensive login flow test - Verifies no redirect loops occur
"""
import requests
from bs4 import BeautifulSoup

def test_complete_auth_flow():
    """Test the complete authentication flow without redirect loops"""
    base_url = 'http://localhost:8000'
    session = requests.Session()
    
    print("=" * 70)
    print("COMPLETE AUTHENTICATION FLOW TEST - No Redirect Loops")
    print("=" * 70)
    
    # Step 1: Verify unauthenticated user cannot access dashboard
    print("\n1. Testing unauthenticated user access to dashboard...")
    print("-" * 70)
    try:
        response = session.get(f'{base_url}/dashboard/', allow_redirects=False, timeout=5)
        if response.status_code == 302:
            redirect_to = response.headers.get('Location', '')
            print(f"✓ Unauthenticated user redirected (Status: 302)")
            print(f"  Redirect to: {redirect_to}")
            if 'login' in redirect_to.lower():
                print("✓ Correctly redirected to login page")
        else:
            print(f"✗ Expected redirect, got status {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Step 2: Get login form and CSRF token
    print("\n2. Fetching login page...")
    print("-" * 70)
    try:
        response = session.get(f'{base_url}/login/', timeout=5)
        if response.status_code != 200:
            print(f"✗ Failed to load login page (Status: {response.status_code})")
            return False
        
        print(f"✓ Login page loaded (Status: 200)")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
        
        if not csrf_input or not csrf_input.get('value'):
            print("✗ CSRF token not found")
            return False
        
        csrf_token = csrf_input.get('value')
        print(f"✓ CSRF token extracted")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    # Step 3: Submit login form
    print("\n3. Submitting login form with Dev:Dev@123...")
    print("-" * 70)
    try:
        login_data = {
            'email': 'Dev',
            'password': 'Dev@123',
            'csrfmiddlewaretoken': csrf_token
        }
        
        response = session.post(
            f'{base_url}/login/',
            data=login_data,
            allow_redirects=False,
            timeout=5
        )
        
        if response.status_code != 302:
            print(f"✗ Expected redirect (302), got {response.status_code}")
            return False
        
        redirect_to = response.headers.get('Location', '')
        print(f"✓ Form submitted (Status: 302)")
        print(f"  Redirect to: {redirect_to}")
        
        if 'dashboard' not in redirect_to.lower():
            print(f"✗ Expected redirect to dashboard, got {redirect_to}")
            return False
        
        print("✓ Correctly redirected to dashboard")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    # Step 4: Verify session is established
    print("\n4. Verifying authenticated session...")
    print("-" * 70)
    try:
        # Check if sessionid cookie is present
        cookies = session.cookies.get_dict()
        if 'sessionid' in cookies:
            print(f"✓ Session cookie established: {cookies['sessionid'][:20]}...")
        else:
            print("✗ No session cookie found")
            return False
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    # Step 5: Access dashboard without redirect loop
    print("\n5. Accessing dashboard after authentication...")
    print("-" * 70)
    try:
        response = session.get(f'{base_url}/dashboard/', allow_redirects=False, timeout=5)
        
        if response.status_code == 200:
            print(f"✓ Dashboard accessed successfully (Status: 200)")
            print("✅ NO REDIRECT LOOP - User authenticated and accessing dashboard")
            return True
        elif response.status_code == 302:
            location = response.headers.get('Location', '')
            print(f"✗ Unexpected redirect to {location}")
            print("❌ REDIRECT LOOP DETECTED!")
            return False
        else:
            print(f"✗ Unexpected status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_accounts_prefixed_path():
    """Test login at /accounts/login/ path"""
    base_url = 'http://localhost:8000'
    session = requests.Session()
    
    print("\n\n" + "=" * 70)
    print("TESTING /accounts/login/ PATH")
    print("=" * 70)
    
    try:
        # Get CSRF token from /accounts/login/
        response = session.get(f'{base_url}/accounts/login/', timeout=5)
        if response.status_code != 200:
            print(f"✗ Failed to load /accounts/login/ (Status: {response.status_code})")
            return False
        
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
        csrf_token = csrf_input.get('value')
        
        # Submit login
        login_data = {
            'email': 'testuser',
            'password': 'testpass123',
            'csrfmiddlewaretoken': csrf_token
        }
        
        response = session.post(
            f'{base_url}/accounts/login/',
            data=login_data,
            allow_redirects=False,
            timeout=5
        )
        
        if response.status_code == 302:
            print(f"✓ Login from /accounts/login/ successful (Status: 302)")
            print(f"  Redirect to: {response.headers.get('Location', 'N/A')}")
            
            # Try accessing dashboard
            dash_response = session.get(f'{base_url}/accounts/dashboard/', timeout=5)
            if dash_response.status_code == 200:
                print("✓ Dashboard accessible after login")
                return True
        
        return False
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == '__main__':
    print("""
╔════════════════════════════════════════════════════════════════════════╗
║     COMPREHENSIVE AUTHENTICATION FLOW TEST - REDIRECT LOOP DETECTION   ║
║              Ensure login doesn't redirect back to login page          ║
╚════════════════════════════════════════════════════════════════════════╝
    """)
    
    test1 = test_complete_auth_flow()
    test2 = test_accounts_prefixed_path()
    
    print("\n\n" + "=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)
    print(f"Complete flow (root /login/):        {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"Accounts path (/accounts/login/):     {'✅ PASS' if test2 else '❌ FAIL'}")
    
    if test1 and test2:
        print("\n✅ ALL TESTS PASSED - LOGIN FIXED!")
        print("\n✨ Key improvements:")
        print("  • Uses absolute path redirects (/accounts/dashboard/) instead of URL names")
        print("  • Eliminates duplicate URL name conflicts from dual includes")
        print("  • Settings.py uses absolute paths for LOGIN_URL")
        print("  • @login_required decorator uses explicit login_url parameter")
        print("  • No more redirect loops to login page")
    else:
        print("\n❌ SOME TESTS FAILED")
