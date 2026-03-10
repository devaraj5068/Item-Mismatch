#!/usr/bin/env python
"""
Debug login form submission issue
"""
import requests
from bs4 import BeautifulSoup

def debug_login_issue():
    base_url = 'http://localhost:8000'
    session = requests.Session()

    print("=" * 70)
    print("DEBUGGING LOGIN FORM SUBMISSION")
    print("=" * 70)

    # Step 1: Get the login page
    print("\n1. Fetching login page...")
    response = session.get(f'{base_url}/login/', timeout=5)
    print(f"Status: {response.status_code}")

    if response.status_code != 200:
        print("❌ Cannot load login page")
        return

    # Parse the form
    soup = BeautifulSoup(response.text, 'html.parser')
    form = soup.find('form')
    if not form:
        print("❌ No form found on login page")
        return

    print("✓ Form found")

    # Check form action
    action = form.get('action', '')
    method = form.get('method', '').upper()
    print(f"✓ Form action: '{action}', method: {method}")

    # Get CSRF token
    csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
    if not csrf_input:
        print("❌ No CSRF token found")
        return

    csrf_token = csrf_input.get('value')
    print(f"✓ CSRF token: {csrf_token[:20]}...")

    # Check input fields
    username_input = soup.find('input', {'name': 'username'})
    password_input = soup.find('input', {'name': 'password'})

    if not username_input:
        print("❌ No username input field")
        return
    if not password_input:
        print("❌ No password input field")
        return

    print("✓ Username and password fields found")

    # Step 2: Submit the form
    print("\n2. Submitting login form with Dev:Dev@123...")

    form_data = {
        'username': 'Dev',
        'password': 'Dev@123',
        'csrfmiddlewaretoken': csrf_token
    }

    print(f"Form data: username='{form_data['username']}', password='***', csrf='{csrf_token[:10]}...'")

    response = session.post(f'{base_url}/login/', data=form_data, allow_redirects=False, timeout=5)

    print(f"Response status: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")

    if response.status_code == 302:
        location = response.headers.get('Location', '')
        print(f"✓ Redirect to: {location}")
        if 'dashboard' in location:
            print("✅ SUCCESS: Redirected to dashboard")
        else:
            print("❌ FAIL: Not redirected to dashboard")
    elif response.status_code == 200:
        # Check if error message is shown
        soup = BeautifulSoup(response.text, 'html.parser')
        error_div = soup.find('div', {'class': 'error-message'})
        if error_div:
            error_text = error_div.get_text().strip()
            print(f"❌ Error message displayed: '{error_text}'")
        else:
            print("❌ Form redisplayed but no error message found")

        # Debug: check what was posted
        print("\nDEBUG: Checking what the view received...")
        # Let's add some debug prints to the view temporarily

    else:
        print(f"❌ Unexpected status code: {response.status_code}")

if __name__ == '__main__':
    debug_login_issue()