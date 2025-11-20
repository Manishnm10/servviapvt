"""
Test Medical Profile Imports
Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): 2025-11-19 11:40:07
Current User's Login: Raghuraam21
"""
import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("\n" + "="*70)
print("  Testing Medical Profile API Imports")
print("="*70)

# Test 1: Import medical_db_operations
print("\n1️⃣ Testing medical.medical_db_operations...")
try:
    from medical.medical_db_operations import (
        create_medical_profile,
        get_medical_profile_by_user_id,
        update_medical_profile,
        delete_medical_profile,
        get_medical_profile_history
    )
    print("   ✅ All functions imported successfully")
    print(f"   - create_medical_profile: {create_medical_profile}")
    print(f"   - get_medical_profile_by_user_id: {get_medical_profile_by_user_id}")
    print(f"   - update_medical_profile: {update_medical_profile}")
    print(f"   - delete_medical_profile: {delete_medical_profile}")
    print(f"   - get_medical_profile_history: {get_medical_profile_history}")
except ImportError as e:
    print(f"   ❌ Import failed: {e}")

# Test 2: Import User model
print("\n2️⃣ Testing database.models.User...")
try:
    from database.models import User
    print(f"   ✅ User model imported: {User}")
except ImportError as e:
    print(f"   ❌ Import failed: {e}")

# Test 3: Import db_conn
print("\n3️⃣ Testing database.database_config.db_conn...")
try:
    from database.database_config import db_conn
    print(f"   ✅ Database connection imported: {db_conn}")
except ImportError as e:
    print(f"   ❌ Import failed: {e}")

# Test 4: Import common utils
print("\n4️⃣ Testing common.utils.get_or_create_user_by_email...")
try:
    from common.utils import get_or_create_user_by_email
    print(f"   ✅ Utils imported: {get_or_create_user_by_email}")
except ImportError as e:
    print(f"   ❌ Import failed: {e}")

# Test 5: Check if database tables exist
print("\n5️⃣ Testing database table access...")
try:
    from database.models import UserMedicalProfile, MedicalProfileAuditLog
    print(f"   ✅ UserMedicalProfile: {UserMedicalProfile}")
    print(f"   ✅ MedicalProfileAuditLog: {MedicalProfileAuditLog}")
except ImportError as e:
    print(f"   ❌ Import failed: {e}")

# Test 6: Try to connect to database
print("\n6️⃣ Testing database connection...")
try:
    from database.database_config import db_conn
    with db_conn:
        print("   ✅ Database connection successful")
except Exception as e:
    print(f"   ❌ Database connection failed: {e}")

print("\n" + "="*70)
print("  Diagnostic Complete")
print("="*70 + "\n")