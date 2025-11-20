"""
Promote User to Admin
Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): 2025-11-19 12:30:48
Current User's Login: Raghuraam21
"""
import sys
from database.models import User
from peewee import DoesNotExist

if len(sys.argv) < 2:
    print("\n❌ Usage: python promote_admin.py <email>")
    print("Example: python promote_admin.py admin@servvia.com\n")
    sys.exit(1)

email = sys.argv[1].strip().lower()

print("\n" + "="*70)
print(f"  Promoting User to Admin: {email}")
print("="*70)

try:
    user = User.get(User.email == email)
    
    print(f"\n✅ User found:")
    print(f"   ID: {user.id}")
    print(f"   Email: {user.email}")
    print(f"   Current Role: {user.role}")
    
    if user.role == 'admin':
        print(f"\n⚠️  User is already an admin!")
    else:
        user.role = 'admin'
        user.save()
        print(f"\n✅ User promoted to admin successfully!")
    
    print("\n" + "="*70 + "\n")

except DoesNotExist:
    print(f"\n❌ User not found: {email}")
    print("💡 User must register first before being promoted")
    print("\n" + "="*70 + "\n")
except Exception as e:
    print(f"\n❌ Error: {e}\n")