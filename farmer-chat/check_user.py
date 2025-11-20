"""
Check User in Database
Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): 2025-11-20 10:01:32
Current User's Login: Raghuraam21
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_core.settings')
django.setup()

from database.models import User

email = 'mohammedayaan2193@gmail.com'

try:
    user = User.get(User.email == email)
    
    print("\n" + "=" * 70)
    print("  User Information")
    print("=" * 70)
    print(f"ID: {user.id}")
    print(f"Email: {user.email}")
    print(f"First Name: {user.first_name}")
    print(f"Last Name: {user.last_name}")
    print(f"Role: {user.role}")
    
    # Check password
    if user.password:
        print(f"Password Hash: {user.password[:30]}... (length: {len(user.password)})")
        print("Password Status: ✅ HAS PASSWORD")
    else:
        print("Password Hash: NULL")
        print("Password Status: ❌ NO PASSWORD")
    
    # Check OAuth provider
    if hasattr(user, 'oauth_provider'):
        print(f"OAuth Provider: {user.oauth_provider}")
    else:
        print("OAuth Provider: None (not an OAuth field)")
    
    print("=" * 70)
    
    # Summary
    if not user.password:
        print("\n⚠️  WARNING: USER HAS NO PASSWORD!")
        print("=" * 70)
        print("This user cannot login with email/password.")
        print("\n📋 Options:")
        print("   1. Delete user and re-register: python delete_user.py")
        print("   2. Set password manually: python set_password.py")
        print("   3. Use Google OAuth login")
        print("=" * 70)
    else:
        print("\n✅ User has a password and can login!")
        print("=" * 70)
        print(f"Login with:")
        print(f"   Email: {email}")
        print(f"   Password: (the password you used)")
        print("=" * 70)
    
    print("\n")
    
except User.DoesNotExist:
    print(f"\n❌ User not found: {email}\n")
except Exception as e:
    print(f"\n❌ Error: {e}\n")
    import traceback
    traceback.print_exc()