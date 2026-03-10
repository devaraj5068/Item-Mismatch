#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trackright_backend.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token

print("=" * 50)
print("Testing Login System")
print("=" * 50)

# Check existing users
all_users = User.objects.all()
print(f"\nAll users in database: {[u.username for u in all_users]}")

# Delete existing Dev user if any
User.objects.filter(username='Dev').delete()
print("\nCleaned up old Dev user")

# Create new Dev user
dev_user = User.objects.create_user(username='Dev', password='Dev@123')
print(f"✓ Created user: {dev_user.username}")
print(f"  - Userid: {dev_user.id}")
print(f"  - is_active: {dev_user.is_active}")

# Test authentication
print("\nTesting authentication...")
auth_user = authenticate(username='Dev', password='Dev@123')
if auth_user:
    print("✓ Authentication SUCCESS")
    token, created = Token.objects.get_or_create(user=auth_user)
    print(f"✓ Token: {token.key}")
else:
    print("✗ Authentication FAILED")

print("\n" + "=" * 50)
