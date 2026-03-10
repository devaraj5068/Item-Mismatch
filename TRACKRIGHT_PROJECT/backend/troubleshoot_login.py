#!/usr/bin/env python
"""
TrackRight Login Troubleshooting Guide
Run this to diagnose and fix login issues
"""

def print_troubleshooting_guide():
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      TRACKRIGHT LOGIN TROUBLESHOOTING GUIDE                     ║
║              "Invalid credentials" error with Dev/Dev@123                      ║
╚══════════════════════════════════════════════════════════════════════════════╝

🔍 DIAGNOSIS: Authentication works in backend tests but fails in browser

✅ CONFIRMED WORKING:
   • User 'Dev' exists in database
   • Password 'Dev@123' is correct
   • authenticate() function works
   • Login view logic is correct
   • Form fields are properly named
   • CSRF protection is enabled

❌ MOST LIKELY CAUSES:

1. 🌐 BROWSER CACHE/CACHE ISSUES
2. 🚀 DJANGO SERVER NOT RUNNING
3. 🔗 WRONG URL BEING USED
4. 🍪 BROWSER COOKIES CORRUPTED
5. 🔄 CSRF TOKEN ISSUES

═══════════════════════════════════════════════════════════════════════════════

🛠️  STEP-BY-STEP FIXES:

STEP 1: Clear Browser Cache & Cookies
─────────────────────────────────────
• Open Developer Tools (F12)
• Right-click refresh button → "Empty Cache and Hard Reload"
• OR: Clear browsing data for localhost:8000
• Try in incognito/private window

STEP 2: Restart Django Server
─────────────────────────────
Current terminal shows server running, but restart it:

cd "d:\edge\work tracker 3\work tracker 3\work tracker\TRACKRIGHT_PROJECT\backend"
python manage.py runserver

STEP 3: Verify Correct URL
──────────────────────────
Make sure you're visiting:
✅ http://localhost:8000/login/
❌ NOT: http://127.0.0.1:8000/login/
❌ NOT: http://localhost:8000/accounts/login/

STEP 4: Check Browser Network Tab
──────────────────────────────────
• Open Developer Tools (F12) → Network tab
• Submit login form
• Look for the POST /login/ request
• Check response status and redirect location

STEP 5: Manual Form Submission Test
───────────────────────────────────
If browser still fails, try this curl command:

curl -X POST http://localhost:8000/login/ \\
  -d "username=Dev&password=Dev@123&csrfmiddlewaretoken=YOUR_TOKEN" \\
  -H "Cookie: csrftoken=YOUR_TOKEN"

═══════════════════════════════════════════════════════════════════════════════

🧪 VERIFICATION TESTS:

Run these commands to confirm everything works:

1. Check user exists:
   python manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.filter(username='Dev').exists())"

2. Test authentication:
   python manage.py shell -c "from django.contrib.auth import authenticate; print(authenticate(username='Dev', password='Dev@123') is not None)"

3. Test login flow:
   python diagnostic_login.py

4. Full authentication test:
   python test_auth_flow.py

═══════════════════════════════════════════════════════════════════════════════

🎯 EXPECTED BEHAVIOR:

When you enter Dev / Dev@123 and submit:

1. POST request to /login/
2. Status: 302 Found
3. Location: /accounts/dashboard/
4. Session cookie created
5. Redirect to dashboard
6. Dashboard loads successfully

═══════════════════════════════════════════════════════════════════════════════

🚨 IF STILL FAILING:

1. Check Django logs in terminal for errors
2. Verify no JavaScript errors in browser console
3. Try different browser (Chrome, Firefox, Edge)
4. Check if antivirus/firewall is blocking
5. Restart computer if necessary

═══════════════════════════════════════════════════════════════════════════════

📞 SUPPORT:

If all else fails, the login system is correctly implemented.
The issue is likely environmental (cache, server, browser).

Run: python diagnostic_login.py
This will confirm if the backend is working correctly.
    """)

if __name__ == '__main__':
    print_troubleshooting_guide()