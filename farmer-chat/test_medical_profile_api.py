"""
Medical Profile API Test Suite
Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): 2025-11-19 11:28:45
Current User's Login: Raghuraam21

Tests all CRUD operations for medical profiles:
- Create profile
- Get profile
- Update profile
- Delete profile
- Consent management
- Audit history
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

def print_separator(title=""):
    """Print a formatted separator"""
    print("\n" + "=" * 70)
    if title:
        print(f"  {title}")
        print("=" * 70)
    else:
        print("=" * 70)


def test_create_medical_profile():
    """Test creating a new medical profile"""
    print_separator("Test 1: Create Medical Profile")
    
    test_data = {
        "email": "john.doe@example.com",
        "has_diabetes": True,
        "has_hypertension": False,
        "has_heart_disease": False,
        "has_kidney_disease": False,
        "has_allergies": True,
        "allergies": ["peanuts", "shellfish", "dairy"],
        "is_pregnant": False,
        "is_breastfeeding": False,
        "current_medications": ["metformin", "aspirin"],
        "consent_given": True
    }
    
    print(f"\n📤 Sending POST request to {BASE_URL}/medical/profile/")
    print(f"📋 Data:")
    print(json.dumps(test_data, indent=2))
    
    try:
        response = requests.post(
            f"{BASE_URL}/medical/profile/",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"\n✅ Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n📊 Response Data:")
            print(json.dumps(data, indent=2))
            
            if data.get('success'):
                print("\n✅ PASS: Medical profile created successfully!")
                profile = data.get('profile', {})
                print(f"   User ID: {profile.get('user_id')}")
                print(f"   Diabetes: {profile.get('has_diabetes')}")
                print(f"   Allergies: {profile.get('allergies')}")
                print(f"   Medications: {profile.get('current_medications')}")
                return True, data
            else:
                print(f"\n❌ FAIL: {data.get('error', 'Unknown error')}")
                return False, None
        else:
            print(f"\n❌ FAIL: HTTP {response.status_code}")
            print(f"Response: {response.text[:300]}")
            return False, None
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False, None


def test_get_medical_profile(email):
    """Test retrieving a medical profile"""
    print_separator("Test 2: Get Medical Profile")
    
    print(f"\n📤 Sending GET request to {BASE_URL}/medical/profile/get/")
    print(f"📋 Email: {email}")
    
    try:
        response = requests.get(
            f"{BASE_URL}/medical/profile/get/",
            params={"email": email},
            timeout=10
        )
        
        print(f"\n✅ Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n📊 Response Data:")
            print(json.dumps(data, indent=2))
            
            if data.get('success') and data.get('profile_exists'):
                profile = data.get('profile', {})
                print(f"\n✅ PASS: Profile retrieved successfully!")
                print(f"   User ID: {profile.get('user_id')}")
                print(f"   Diabetes: {profile.get('has_diabetes')}")
                print(f"   Allergies: {profile.get('allergies')}")
                print(f"   Medications: {profile.get('current_medications')}")
                return True, data
            else:
                print(f"\n⚠️ Profile does not exist or error occurred")
                return False, None
        else:
            print(f"\n❌ FAIL: HTTP {response.status_code}")
            return False, None
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False, None


def test_update_medical_profile(email):
    """Test updating an existing medical profile"""
    print_separator("Test 3: Update Medical Profile")
    
    update_data = {
        "email": email,
        "has_diabetes": True,
        "has_hypertension": True,  # Changed from False to True
        "has_heart_disease": False,
        "allergies": ["peanuts", "shellfish", "dairy", "eggs"],  # Added eggs
        "current_medications": ["metformin", "aspirin", "lisinopril"]  # Added lisinopril
    }
    
    print(f"\n📤 Sending POST request to {BASE_URL}/medical/profile/")
    print(f"📋 Update Data:")
    print(json.dumps(update_data, indent=2))
    
    try:
        response = requests.post(
            f"{BASE_URL}/medical/profile/",
            json=update_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"\n✅ Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n📊 Response Data:")
            print(json.dumps(data, indent=2))
            
            if data.get('success') and data.get('action') == 'updated':
                profile = data.get('profile', {})
                print(f"\n✅ PASS: Profile updated successfully!")
                print(f"   Hypertension: {profile.get('has_hypertension')} (should be True)")
                print(f"   Allergies: {profile.get('allergies')} (should include eggs)")
                print(f"   Medications: {profile.get('current_medications')} (should include lisinopril)")
                return True, data
            else:
                print(f"\n❌ FAIL: {data.get('error', 'Update failed')}")
                return False, None
        else:
            print(f"\n❌ FAIL: HTTP {response.status_code}")
            return False, None
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False, None


def test_get_profile_history(email):
    """Test retrieving profile update history"""
    print_separator("Test 4: Get Profile History (Audit Log)")
    
    print(f"\n📤 Sending GET request to {BASE_URL}/medical/history/")
    print(f"📋 Email: {email}")
    
    try:
        response = requests.get(
            f"{BASE_URL}/medical/history/",
            params={"email": email, "limit": 10},
            timeout=10
        )
        
        print(f"\n✅ Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n📊 Response Data:")
            print(json.dumps(data, indent=2))
            
            if data.get('success'):
                history = data.get('history', [])
                print(f"\n✅ PASS: History retrieved successfully!")
                print(f"   Total Entries: {data.get('total_entries', 0)}")
                
                for i, entry in enumerate(history[:3], 1):  # Show first 3
                    print(f"\n   Entry {i}:")
                    print(f"      Action: {entry.get('action')}")
                    print(f"      Timestamp: {entry.get('timestamp')}")
                    print(f"      Accessed By: {entry.get('accessed_by')}")
                
                return True, data
            else:
                print(f"\n⚠️ No history found or error occurred")
                return False, None
        else:
            print(f"\n❌ FAIL: HTTP {response.status_code}")
            return False, None
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False, None


def test_update_consent(email, consent_given):
    """Test updating user consent"""
    print_separator(f"Test 5: Update Consent (consent={'granted' if consent_given else 'revoked'})")
    
    consent_data = {
        "email": email,
        "consent_given": consent_given
    }
    
    print(f"\n📤 Sending POST request to {BASE_URL}/medical/consent/")
    print(f"📋 Data:")
    print(json.dumps(consent_data, indent=2))
    
    try:
        response = requests.post(
            f"{BASE_URL}/medical/consent/",
            json=consent_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"\n✅ Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n📊 Response Data:")
            print(json.dumps(data, indent=2))
            
            if data.get('success'):
                print(f"\n✅ PASS: Consent {'granted' if consent_given else 'revoked'} successfully!")
                print(f"   Consent Status: {data.get('consent_given')}")
                print(f"   Consent Date: {data.get('consent_date')}")
                return True, data
            else:
                print(f"\n❌ FAIL: {data.get('error', 'Unknown error')}")
                return False, None
        else:
            print(f"\n❌ FAIL: HTTP {response.status_code}")
            return False, None
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False, None


def test_delete_medical_profile(email):
    """Test deleting a medical profile"""
    print_separator("Test 6: Delete Medical Profile")
    
    print(f"\n📤 Sending DELETE request to {BASE_URL}/medical/profile/delete/")
    print(f"📋 Email: {email}")
    
    try:
        response = requests.delete(
            f"{BASE_URL}/medical/profile/delete/",
            params={"email": email},
            timeout=10
        )
        
        print(f"\n✅ Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n📊 Response Data:")
            print(json.dumps(data, indent=2))
            
            if data.get('success'):
                print(f"\n✅ PASS: Profile deleted successfully!")
                return True, data
            else:
                print(f"\n❌ FAIL: {data.get('error', 'Unknown error')}")
                return False, None
        else:
            print(f"\n❌ FAIL: HTTP {response.status_code}")
            return False, None
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False, None


def run_all_tests():
    """Run all medical profile API tests"""
    print("\n" + "="*70)
    print("  Medical Profile API Test Suite")
    print("  Current Date and Time (UTC): 2025-11-19 11:28:45")
    print("  Current User: Raghuraam21")
    print("="*70)
    
    test_email = "john.doe@example.com"
    results = []
    
    # Test 1: Create profile
    success, data = test_create_medical_profile()
    results.append(("Create Profile", success))
    time.sleep(1)
    
    # Test 2: Get profile
    success, data = test_get_medical_profile(test_email)
    results.append(("Get Profile", success))
    time.sleep(1)
    
    # Test 3: Update profile
    success, data = test_update_medical_profile(test_email)
    results.append(("Update Profile", success))
    time.sleep(1)
    
    # Test 4: Get history
    success, data = test_get_profile_history(test_email)
    results.append(("Get History", success))
    time.sleep(1)
    
    # Test 5: Update consent
    success, data = test_update_consent(test_email, True)
    results.append(("Grant Consent", success))
    time.sleep(1)
    
    # Test 6: Revoke consent
    success, data = test_update_consent(test_email, False)
    results.append(("Revoke Consent", success))
    time.sleep(1)
    
    # Test 7: Delete profile
    success, data = test_delete_medical_profile(test_email)
    results.append(("Delete Profile", success))
    
    # Print summary
    print_separator("TEST SUMMARY")
    
    total = len(results)
    passed = sum(1 for _, success in results if success)
    failed = total - passed
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests PASSED! 🎉")
    else:
        print(f"⚠️ {failed} test(s) FAILED")
    
    print("\n📋 Detailed Results:")
    for test_name, success in results:
        status_icon = "✅" if success else "❌"
        print(f"{status_icon} {test_name}")
    
    print("\n" + "="*70)
    print("Test completed at: 2025-11-19 11:28:45 UTC")
    print("="*70 + "\n")


if __name__ == "__main__":
    run_all_tests()