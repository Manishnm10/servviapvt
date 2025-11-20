"""
Database Migration: Add role field to User model
Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): 2025-11-19 12:28:13
Current User's Login: Raghuraam21
"""
from database.models import User, db_conn
from playhouse.migrate import PostgresqlMigrator, migrate
from peewee import CharField

print("\n" + "="*70)
print("  Database Migration: Adding 'role' field to User model")
print("="*70)

try:
    migrator = PostgresqlMigrator(db_conn)
    
    # Add role field with default 'patient'
    role_field = CharField(max_length=20, default='patient')
    
    print("\n1️⃣ Adding 'role' column to 'user' table...")
    
    migrate(
        migrator.add_column('user', 'role', role_field)
    )
    
    print("   ✅ Column added successfully")
    
    # Set default role for existing users
    print("\n2️⃣ Setting default role for existing users...")
    
    update_count = User.update(role='patient').where(User.role.is_null(True)).execute()
    
    print(f"   ✅ Updated {update_count} existing user(s) to 'patient' role")
    
    # Create first admin user
    print("\n3️⃣ Creating admin user (if needed)...")
    
    try:
        admin_email = "admin@servvia.com"
        admin = User.get(User.email == admin_email)
        admin.role = 'admin'
        admin.save()
        print(f"   ✅ Set {admin_email} as admin")
    except:
        print(f"   ℹ️  No admin user found. You can promote one later.")
    
    print("\n" + "="*70)
    print("  ✅ Migration Complete!")
    print("="*70)
    print("\n💡 Role Field Added:")
    print("   - Default: 'patient'")
    print("   - Options: 'patient', 'admin'")
    print("\n" + "="*70 + "\n")
    
except Exception as e:
    print(f"\n❌ Migration Error: {e}")
    
    if "already exists" in str(e).lower():
        print("\n✅ Role field already exists - skipping migration")
        print("="*70 + "\n")
    else:
        print("\n⚠️  Manual fix needed:")
        print("   Run this SQL in your database:")
        print("   ALTER TABLE \"user\" ADD COLUMN role VARCHAR(20) DEFAULT 'patient';")
        print("="*70 + "\n")