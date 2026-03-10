#!/usr/bin/env python
"""
Test the proper Django authentication flow as implemented
"""
import requests
from bs4 import BeautifulSoup

def test_proper_auth_flow():
    """Test the authentication flow as per user requirements"""
    base_url = 'http://localhost:8000'
    session = requests.Session()
    
    print("=" * 70)
    print("TESTING PROPER DJANGO AUTHENTICATION FLOW")
    print("=" * 70)
    
    # Step 1: Access login page
    print("\n1. Accessing /login/ page...")
    response = session.get(f'{base_url}/login/', timeout=5)
    if response.status_code != 200:
        print(f"✗ Failed to load login page: {response.status_code}")
        return False
    print("✓ Login page loaded (200 OK)")
    
    # Extract CSRF token
    soup = BeautifulSoup(response.text, 'html.parser')
    csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
    if not csrf_input:
        print("✗ CSRF token not found")
        return False
    csrf_token = csrf_input.get('value')
    print("✓ CSRF token extracted")
    
    # Check form field names
    username_input = soup.find('input', {'name': 'username'})
    password_input = soup.find('input', {'name': 'password'})
    if not username_input or not password_input:
        print("✗ Form fields not properly named")
        return False
    print("✓ Form has correct field names: username, password")
    
    # Step 2: Submit login form with correct credentials
    print("\n2. Submitting login form with Dev:Dev@123...")
    login_data = {
        'username': 'Dev',
        'password': 'Dev@123',
        'csrfmiddlewaretoken': csrf_token
    }
    
    response = session.post(f'{base_url}/login/', data=login_data, allow_redirects=False, timeout=5)
    
    if response.status_code != 302:
        print(f"✗ Expected redirect (302), got {response.status_code}")
        return False
    
    redirect_location = response.headers.get('Location', '')
    print(f"✓ Form submitted, redirect to: {redirect_location}")
    
    if 'dashboard' not in redirect_location.lower():
        print(f"✗ Expected redirect to dashboard, got {redirect_location}")
        return False
    
    # Step 3: Verify session persistence - access dashboard
    print("\n3. Verifying session persistence - accessing dashboard...")
    response = session.get(f'{base_url}/dashboard/', timeout=5)
    
    if response.status_code != 200:
        print(f"✗ Dashboard access failed: {response.status_code}")
        return False
    
    print("✓ Dashboard loaded successfully (200 OK)")
    print("✓ Session is persisting - user remains logged in")
    
    # Step 4: Test logout
    print("\n4. Testing logout...")
    response = session.get(f'{base_url}/logout/', allow_redirects=False, timeout=5)
    
    if response.status_code != 302:
        print(f"✗ Logout redirect failed: {response.status_code}")
        return False
    
    logout_redirect = response.headers.get('Location', '')
    print(f"✓ Logout successful, redirect to: {logout_redirect}")
    
    # Step 5: Verify logout worked - dashboard should redirect to login
    print("\n5. Verifying logout - dashboard should require login...")
    response = session.get(f'{base_url}/dashboard/', allow_redirects=False, timeout=5)
    
    if response.status_code != 302:
        print(f"✗ Expected redirect after logout, got {response.status_code}")
        return False
    
    redirect_to_login = response.headers.get('Location', '')
    if 'login' not in redirect_to_login.lower():
        print(f"✗ Expected redirect to login, got {redirect_to_login}")
        return False
    
    print("✓ Dashboard correctly redirects to login after logout")
    
    print("\n" + "=" * 70)
    print("✅ AUTHENTICATION FLOW WORKING CORRECTLY")
    print("=" * 70)
    print("""
✓ Login page loads at /login/
✓ Form has correct field names (username, password)
✓ CSRF protection enabled
✓ Correct credentials authenticate user
✓ login(request, user) creates session
✓ Redirect to /dashboard/ after login
✓ Session persists across requests
✓ Dashboard protected with @login_required
✓ Logout clears session
✓ Redirect to /login/ after logout
✓ Protected pages redirect to login when not authenticated
    """)
    return True

if __name__ == '__main__':
    success = test_proper_auth_flow()
    if not success:
        print("\n❌ AUTHENTICATION FLOW HAS ISSUES")
    else:
        print("\n🎉 Django authentication flow is properly implemented!")