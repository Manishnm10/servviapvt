"""
Delete User from Database (Safe Version)
Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): 2025-11-20 10:10:38
Current User's Login: Raghuraam21
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_core.settings')
django.setup()

from database.models import User
from peewee import Model

email = 'mohammedayaan2193@gmail.com'

try:
    user = User.get(User.email == email)
    
    print("\n" + "=" * 70)
    print("  DELETE USER (WITH CASCADE)")
    print("=" * 70)
    print(f"ID: {user.id}")
    print(f"Name: {user.first_name} {user.last_name}")
    print(f"Email: {user.email}")
    print(f"Role: {user.role}")
    print(f"Password: {'NULL (No password!)' if not user.password else 'Has password'}")
    print("=" * 70)
    
    confirm = input("\n⚠️  Type 'DELETE' to delete user and ALL related data: ")
    
    if confirm == 'DELETE':
        print("\n🗑️ Deleting user and related data...")
        
        # Use recursive delete to handle foreign keys
        try:
            # Delete with cascade (automatically deletes related records)
            user.delete_instance(recursive=True)
            print(f"   ✅ Deleted user and all related data: {email}")
        except Exception as e:
            print(f"   ❌ Error during deletion: {e}")
            print("\n   Trying alternative method...")
            
            # Alternative: Delete using raw SQL
            try:
                from database.models import db
                
                # Delete from audit logs
                db.execute_sql(
                    "DELETE FROM medical_profile_audit_log WHERE user_id = %s",
                    (str(user.id),)
                )
                print("   ✅ Deleted audit logs")
                
                # Delete from medical profiles
                db.execute_sql(
                    "DELETE FROM medical_profile WHERE user_id = %s",
                    (str(user.id),)
                )
                print("   ✅ Deleted medical profiles")
                
                # Delete user
                db.execute_sql(
                    "DELETE FROM \"user\" WHERE id = %s",
                    (str(user.id),)
                )
                print(f"   ✅ Deleted user: {email}")
                
            except Exception as e2:
                print(f"   ❌ Alternative method also failed: {e2}")
                raise
        
        print("\n✅ USER DELETED SUCCESSFULLY!")
        print("\n🎯 Next steps:")
        print("=" * 70)
        print("1. Clear browser localStorage:")
        print("   - Press F12 in browser")
        print("   - Type: localStorage.clear();")
        print("   - Press Enter")
        print("")
        print("2. Reload browser:")
        print("   - Type: location.reload();")
        print("")
        print("3. Register new account:")
        print("   - Go to: http://localhost:8000/register/")
        print(f"   - Email: {email}")
        print("   - Password: Ayaan@123")
        print("")
        print("4. Should work perfectly this time! ✅")
        print("=" * 70 + "\n")
    else:
        print(f"\n❌ Deletion cancelled. You typed: '{confirm}'")
        print("   (You must type exactly: DELETE)")
        print("=" * 70 + "\n")
        
except User.DoesNotExist:
    print(f"\n❌ User not found: {email}")
    print("User may have already been deleted.")
    print("=" * 70 + "\n")
except Exception as e:
    print(f"\n❌ Error: {e}\n")
    import traceback
    traceback.print_exc()