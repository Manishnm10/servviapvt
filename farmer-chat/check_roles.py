"""
Check Current User Roles
Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): 2025-11-19 12:30:48
Current User's Login: Raghuraam21
"""
from database.models import User

print("\n" + "="*70)
print("  Current User Role Status")
print("="*70)

# Get all users
users = list(User.select())

if not users:
    print("\n⚠️  No users in database yet")
else:
    print(f"\n📊 Found {len(users)} user(s):\n")
    
    for user in users:
        role = getattr(user, 'role', 'NOT SET')
        print(f"   Email: {user.email}")
        print(f"   Role:  {role}")
        print(f"   ID:    {user.id}")
        print()

# Check if any admins exist
admin_count = User.select().where(User.role == 'admin').count()
patient_count = User.select().where(User.role == 'patient').count()
no_role_count = User.select().where(User.role.is_null(True)).count()

print("="*70)
print("  Role Summary")
print("="*70)
print(f"\n   👤 Patients: {patient_count}")
print(f"   👨‍⚕️ Admins:   {admin_count}")
print(f"   ❓ No Role:  {no_role_count}")

if admin_count == 0:
    print("\n⚠️  No admin users found!")
    print("💡 To create an admin, run:")
    print("   python promote_admin.py admin@servvia.com")

print("\n" + "="*70 + "\n")