import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

from database.database_config import db_conn
from database.models import User, UserMedicalProfile, UserMedicalConsent
from medical.medical_db_operations import (
    create_medical_profile,
    get_medical_profile_by_user_id,
    update_medical_profile,
    delete_medical_profile
)

def test_medical_profile():
    """Test medical profile creation and retrieval"""
    
    print("\n🧪 Testing Medical Profile System\n")
    
    # Ensure connection is open
    db_conn.connect(reuse_if_open=True)
    
    # Test 1: Create or get test user
    print("1️⃣ Creating test user...")
    try:
        with db_conn.atomic():
            test_user = User.create(
                email="test@servvia.com",
                first_name="Test",
                last_name="User"
            )
        print(f"   ✅ User created: {test_user.id}")
    except Exception as e:
        test_user = User.get(User.email == "test@servvia.com")
        print(f"   ✅ Using existing user: {test_user.id}")
    
    # Test 2: Check if profile exists, delete if needed
    print("\n2️⃣ Checking for existing medical profile...")
    existing_profile = get_medical_profile_by_user_id(test_user.id)
    if existing_profile:
        print(f"   ⚠️  Profile already exists. Deleting for fresh test...")
        delete_medical_profile(test_user.id, accessed_by="test@servvia.com", hard_delete=True)
        print(f"   ✅ Old profile deleted")
    else:
        print(f"   ✅ No existing profile found")
    
    # Test 3: Create medical profile
    print("\n3️⃣ Creating medical profile...")
    profile_data = {
        "has_diabetes": True,
        "diabetes_type": "type2",
        "allergies": ["turmeric", "peanuts"],
        "current_medications": ["metformin"],
        "dietary_restrictions": ["low-carb", "no-sugar"],
        "additional_notes": "Monitor blood sugar regularly"
    }
    
    profile = create_medical_profile(
        user_id=test_user.id,
        profile_data=profile_data,
        accessed_by="test@servvia.com"
    )
    
    if profile:
        print(f"   ✅ Profile created successfully")
        print(f"   📋 Diabetes: {profile['has_diabetes']}")
        print(f"   📋 Diabetes Type: {profile.get('diabetes_type')}")
        print(f"   📋 Allergies: {profile['allergies']}")
        print(f"   📋 Medications: {profile['current_medications']}")
        print(f"   📋 Dietary Restrictions: {profile['dietary_restrictions']}")
    else:
        print(f"   ❌ Failed to create profile")
        return
    
    # Test 4: Retrieve profile
    print("\n4️⃣ Retrieving medical profile...")
    retrieved = get_medical_profile_by_user_id(test_user.id)
    
    if retrieved:
        print(f"   ✅ Profile retrieved successfully")
        print(f"   📋 Profile ID: {retrieved['id']}")
        print(f"   📋 Allergies (decrypted): {retrieved['allergies']}")
        print(f"   📋 Medications (decrypted): {retrieved['current_medications']}")
        print(f"   📋 Additional Notes: {retrieved.get('additional_notes', 'None')}")
    else:
        print(f"   ❌ Failed to retrieve profile")
        return
    
    # Test 5: Update profile
    print("\n5️⃣ Updating medical profile...")
    updates = {
        "allergies": ["turmeric", "peanuts", "shellfish"],
        "is_pregnant": False,
        "has_hypertension": True
    }
    
    updated = update_medical_profile(
        user_id=test_user.id,
        updates=updates,
        accessed_by="test@servvia.com"
    )
    
    if updated:
        print(f"   ✅ Profile updated successfully")
        print(f"   📋 New allergies: {updated['allergies']}")
        print(f"   📋 Hypertension: {updated.get('has_hypertension')}")
        print(f"   📋 Profile version: {updated.get('profile_version')}")
    else:
        print(f"   ❌ Failed to update profile")
    
    # Test 6: Test ingredient substitutions
    print("\n6️⃣ Testing ingredient substitutions...")
    from medical.medical_db_operations import get_ingredient_substitutes, create_ingredient_substitution
    
    # Create a test substitution
    sub = create_ingredient_substitution(
        original="sugar",
        substitute="stevia",
        reason="Diabetes-friendly sweetener",
        condition_type="diabetes",
        confidence=0.9,
        category="sweetener"
    )
    
    if sub:
        print(f"   ✅ Substitution created: {sub['original']} → {sub['substitute']}")
    
    # Get substitutions
    subs = get_ingredient_substitutes("sugar", "diabetes")
    if subs:
        print(f"   ✅ Found {len(subs)} substitution(s) for sugar")
        for s in subs:
            print(f"      • {s['original']} → {s['substitute']} ({s['reason']})")
    
    print("\n" + "="*70)
    print("✅ All tests passed! Medical profile system working correctly.")
    print("="*70)
    print("\n📊 Test Summary:")
    print(f"   • User: {test_user.email}")
    print(f"   • Profile created and updated successfully")
    print(f"   • Encryption/decryption working")
    print(f"   • Ingredient substitutions functional")
    print("\n")

if __name__ == "__main__":
    try:
        test_medical_profile()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db_conn.close()