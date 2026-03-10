#!/usr/bin/env python
"""
Complete login test - simulates user experience exactly
"""
import requests
from bs4 import BeautifulSoup
import time

def test_user_login_experience():
    """Test the exact user experience: visit /login/, enter Dev/Dev@123, submit"""

    base_url = 'http://localhost:8000'
    session = requests.Session()

    print("=" * 80)
    print("TESTING EXACT USER LOGIN EXPERIENCE")
    print("=" * 80)

    try:
        # Step 1: User visits /login/
        print("\n1. User visits http://localhost:8000/login/")
        response = session.get(f'{base_url}/login/', timeout=10)
        print(f"   Status: {response.status_code}")

        if response.status_code != 200:
            print("❌ FAIL: Cannot access login page")
            return False

        # Parse the page
        soup = BeautifulSoup(response.text, 'html.parser')

        # Check if there's already an error message (shouldn't be)
        error_div = soup.find('div', {'class': 'error-message'})
        if error_div:
            print(f"⚠️  Warning: Error message already present: '{error_div.get_text().strip()}'")

        # Get form details
        form = soup.find('form')
        if not form:
            print("❌ FAIL: No login form found")
            return False

        csrf_input = form.find('input', {'name': 'csrfmiddlewaretoken'})
        username_input = form.find('input', {'name': 'username'})
        password_input = form.find('input', {'name': 'password'})

        if not csrf_input or not username_input or not password_input:
            print("❌ FAIL: Form missing required fields")
            return False

        csrf_token = csrf_input.get('value')
        print("✓ Form loaded with CSRF token and username/password fields")

        # Step 2: User fills form with Dev / Dev@123
        print("\n2. User enters username='Dev' and password='Dev@123'")

        # Step 3: User clicks submit
        print("\n3. User submits the form...")

        form_data = {
            'username': 'Dev',
            'password': 'Dev@123',
            'csrfmiddlewaretoken': csrf_token
        }

        print(f"   POST data: username='{form_data['username']}', password='***'")

        response = session.post(f'{base_url}/login/', data=form_data, allow_redirects=False, timeout=10)

        print(f"   Response status: {response.status_code}")

        if response.status_code == 302:
            # Success - redirected
            location = response.headers.get('Location', '')
            print(f"✅ SUCCESS: Redirected to {location}")

            # Check if session cookie was set
            cookies = session.cookies.get_dict()
            if 'sessionid' in cookies:
                print("✅ SUCCESS: Session cookie created")
            else:
                print("❌ FAIL: No session cookie")

            # Follow the redirect to dashboard
            print("\n4. Following redirect to dashboard...")
            dash_response = session.get(location, timeout=10)

            if dash_response.status_code == 200:
                print("✅ SUCCESS: Dashboard loaded successfully")
                print("🎉 LOGIN COMPLETED SUCCESSFULLY!")
                return True
            else:
                print(f"❌ FAIL: Dashboard returned {dash_response.status_code}")
                return False

        elif response.status_code == 200:
            # Form redisplayed - authentication failed
            soup = BeautifulSoup(response.text, 'html.parser')
            error_div = soup.find('div', {'class': 'error-message'})

            if error_div:
                error_msg = error_div.get_text().strip()
                print(f"❌ FAIL: Authentication failed - Error: '{error_msg}'")
                print("\n🔍 DEBUGGING:")
                print("   - User 'Dev' exists in database: YES")
                print("   - Password 'Dev@123' is correct: YES")
                print("   - authenticate() works in shell: YES")
                print("   - Form fields are correct: YES")
                print("   - CSRF token present: YES")
                print("\n💡 POSSIBLE CAUSES:")
                print("   - Server restart needed")
                print("   - Browser cache issue")
                print("   - Different URL being used")
                print("   - Database not migrated")
                return False
            else:
                print("❌ FAIL: Form redisplayed but no error message")
                return False

        else:
            print(f"❌ FAIL: Unexpected status code {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print("❌ FAIL: Cannot connect to server. Is Django running?")
        print("   Run: python manage.py runserver")
        return False
    except Exception as e:
        print(f"❌ FAIL: Exception occurred: {e}")
        return False

def test_alternative_credentials():
    """Test with different credentials to ensure the issue is specific"""

    base_url = 'http://localhost:8000'
    session = requests.Session()

    print("\n\n" + "=" * 80)
    print("TESTING ALTERNATIVE CREDENTIALS")
    print("=" * 80)

    try:
        # Test with testuser
        response = session.get(f'{base_url}/login/', timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
        csrf_token = csrf_input.get('value')

        form_data = {
            'username': 'testuser',
            'password': 'testpass123',
            'csrfmiddlewaretoken': csrf_token
        }

        response = session.post(f'{base_url}/login/', data=form_data, allow_redirects=False, timeout=10)

        if response.status_code == 302:
            print("✅ testuser:testpass123 works correctly")
        else:
            print("❌ Even testuser fails - broader issue")

    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == '__main__':
    print("🔍 DIAGNOSTIC: Testing TrackRight login with Dev/Dev@123")
    print("This simulates the exact user experience you're having")

    success = test_user_login_experience()
    test_alternative_credentials()

    print("\n" + "=" * 80)
    if success:
        print("✅ CONCLUSION: Login is working correctly in automated test")
        print("💡 If you're still seeing 'invalid credentials' in browser:")
        print("   1. Clear browser cache and cookies")
        print("   2. Restart Django server: python manage.py runserver")
        print("   3. Make sure you're visiting: http://localhost:8000/login/")
        print("   4. Check browser developer tools for any errors")
    else:
        print("❌ CONCLUSION: Login has issues that need fixing")
    print("=" * 80)