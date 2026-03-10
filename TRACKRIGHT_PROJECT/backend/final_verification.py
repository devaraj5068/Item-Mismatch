#!/usr/bin/env python
"""
Final verification: Login should work without redirecting to /accounts/login/
"""
import requests
from bs4 import BeautifulSoup

def final_test():
    base_url = 'http://localhost:8000'
    session = requests.Session()

    print("=" * 80)
    print("FINAL VERIFICATION: LOGIN AT /login/ WITH Dev/Dev@123")
    print("=" * 80)

    # Access /login/
    print("\n1. Accessing http://localhost:8000/login/...")
    response = session.get(f'{base_url}/login/', timeout=5)
    print(f"   Status: {response.status_code}")

    if response.status_code != 200:
        print("❌ Cannot access /login/")
        return False

    # Check if the page contains redirect JavaScript
    if 'window.location.href' in response.text:
        print("❌ Page contains redirect JavaScript - issue not fixed")
        return False

    print("✓ Page loads without redirect JavaScript")

    # Get CSRF token
    soup = BeautifulSoup(response.text, 'html.parser')
    csrf = soup.find('input', {'name': 'csrfmiddlewaretoken'})
    if not csrf:
        print("❌ No CSRF token")
        return False

    csrf_token = csrf.get('value')
    print("✓ CSRF token present")

    # Submit login
    print("\n2. Submitting login form with Dev/Dev@123...")
    data = {
        'username': 'Dev',
        'password': 'Dev@123',
        'csrfmiddlewaretoken': csrf_token
    }

    response = session.post(f'{base_url}/login/', data=data, allow_redirects=False, timeout=5)
    print(f"   Response status: {response.status_code}")

    if response.status_code != 302:
        print(f"❌ Expected redirect (302), got {response.status_code}")
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            error = soup.find('div', {'class': 'error-message'})
            if error:
                print(f"❌ Authentication failed: {error.get_text().strip()}")
            else:
                print("❌ Form redisplayed without error - unknown issue")
        return False

    location = response.headers.get('Location', '')
    print(f"   Redirect location: {location}")

    if 'dashboard' not in location.lower():
        print(f"❌ Not redirecting to dashboard: {location}")
        if 'accounts/login' in location:
            print("❌ STILL REDIRECTING TO /accounts/login/ - ISSUE NOT FIXED")
        return False

    print("✅ SUCCESS: Redirected to dashboard")

    # Verify dashboard access
    print("\n3. Verifying dashboard access...")
    dash_response = session.get(location, timeout=5)
    if dash_response.status_code == 200:
        print("✅ SUCCESS: Dashboard loaded successfully")
        print("\n🎉 LOGIN ISSUE FIXED!")
        print("   - No more redirect to /accounts/login/")
        print("   - Authentication works correctly")
        print("   - Frontend JS no longer interferes")
        return True
    else:
        print(f"❌ Dashboard access failed: {dash_response.status_code}")
        return False

if __name__ == '__main__':
    success = final_test()
    if not success:
        print("\n❌ LOGIN ISSUE PERSISTS")
    print("\n" + "=" * 80)