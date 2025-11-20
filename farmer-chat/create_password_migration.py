"""
Add password field to User model - Final Version with Quoted Table Name
Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): 2025-11-19 16:47:21
Current User's Login: Raghuraam21
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_core.settings')
django.setup()

print("\n" + "=" * 70)
print("  Adding password field to User model")
print("  Current Date and Time (UTC): 2025-11-19 16:47:21")
print("=" * 70)

try:
    from database.models import User
    
    db = User._meta.database
    
    print(f"\n✅ Connected to database: {db.database}")
    print(f"✅ Table name: {User._meta.table_name}")
    
    # IMPORTANT: "user" is a reserved word in PostgreSQL
    # Must use double quotes around it
    table_name = User._meta.table_name
    
    print(f"\n🔍 Checking if password field exists in '{table_name}' table...")
    
    cursor = db.execute_sql(f"""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='{table_name}' AND column_name='password'
    """)
    
    result = cursor.fetchone()
    
    if result:
        print("\n✅ Password field already exists in database!")
        print("   No migration needed.")
    else:
        print("\n📝 Adding password field...")
        
        # Use double quotes around "user" since it's a reserved word
        db.execute_sql(f"""
            ALTER TABLE "{table_name}" 
            ADD COLUMN password VARCHAR(255) NULL
        """)
        
        print("✅ Password field added successfully!")
    
    # Verify table structure
    print(f"\n🔍 Verifying '{table_name}' table structure...")
    
    cursor = db.execute_sql(f"""
        SELECT column_name, data_type, character_maximum_length, is_nullable
        FROM information_schema.columns 
        WHERE table_name='{table_name}'
        ORDER BY ordinal_position
    """)
    
    print("\n📋 Current User table schema:")
    print("-" * 70)
    print(f"{'Column':<25} {'Type':<20} {'Length':<10} {'Nullable':<10}")
    print("-" * 70)
    
    has_password_column = False
    for row in cursor.fetchall():
        col_name, data_type, max_length, nullable = row
        length_str = str(max_length) if max_length else "N/A"
        print(f"{col_name:<25} {data_type:<20} {length_str:<10} {nullable:<10}")
        
        if col_name == 'password':
            has_password_column = True
    
    print("-" * 70)
    
    if has_password_column:
        print("\n✅ Password column confirmed in database!")
        
        # Check how many users exist
        user_count = User.select().count()
        print(f"\n📊 Database Statistics:")
        print(f"   Total users: {user_count}")
        
        if user_count > 0:
            users_with_pwd = User.select().where(User.password.is_null(False)).count()
            print(f"   Users with password: {users_with_pwd}")
            print(f"   Users without password (OAuth): {user_count - users_with_pwd}")
    else:
        print("\n⚠️ Password column not found in database schema")
    
    print("\n" + "=" * 70)
    print("✅ Migration completed successfully!")
    print("=" * 70 + "\n")

except Exception as e:
    print(f"\n❌ Error: {e}")
    print(f"🔍 Error type: {type(e).__name__}")
    
    import traceback
    print("\n📋 Full traceback:")
    traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("💡 Manual Fix:")
    print("=" * 70)
    print("\nRun this in PostgreSQL (with quotes around 'user'):")
    print('   ALTER TABLE "user" ADD COLUMN password VARCHAR(255);')
    print("\n" + "=" * 70 + "\n")