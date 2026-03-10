#!/usr/bin/env python
"""
Test what happens when login fails
"""
import requests
from bs4 import BeautifulSoup

def test_failed_login():
    base_url = 'http://localhost:8000'
    session = requests.Session()

    print("=" * 70)
    print("TESTING FAILED LOGIN BEHAVIOR")
    print("=" * 70)

    # Get login page
    response = session.get(f'{base_url}/login/', timeout=5)
    soup = BeautifulSoup(response.text, 'html.parser')
    csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
    csrf_token = csrf_input.get('value')

    # Submit with wrong credentials
    print("\n1. Submitting with WRONG credentials...")
    form_data = {
        'username': 'Dev',
        'password': 'WRONG_PASSWORD',
        'csrfmiddlewaretoken': csrf_token
    }

    response = session.post(f'{base_url}/login/', data=form_data, allow_redirects=False, timeout=5)

    print(f"Response status: {response.status_code}")
    print(f"Response location: {response.headers.get('Location', 'None')}")

    if response.status_code == 200:
        print("✓ Correctly renders login page again (status 200)")
        soup = BeautifulSoup(response.text, 'html.parser')
        error_div = soup.find('div', {'class': 'error-message'})
        if error_div:
            print(f"✓ Error message displayed: '{error_div.get_text().strip()}'")
        else:
            print("❌ No error message found")
    elif response.status_code == 302:
        location = response.headers.get('Location', '')
        print(f"❌ Unexpected redirect to: {location}")
        if 'accounts/login' in location:
            print("❌ Redirecting to /accounts/login/ - this is the issue!")
    else:
        print(f"❌ Unexpected status: {response.status_code}")

    # Test accessing protected page when not logged in
    print("\n2. Testing access to protected page when not logged in...")
    response = session.get(f'{base_url}/dashboard/', allow_redirects=False, timeout=5)

    print(f"Response status: {response.status_code}")
    location = response.headers.get('Location', '')
    if location:
        print(f"Redirect to: {location}")
        if 'login' in location:
            print("✓ Correctly redirects to login")
        else:
            print("❌ Not redirecting to login")

if __name__ == '__main__':
    test_failed_login()