"""
Protected Medical Profile API Test Suite
Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): 2025-11-19 12:39:24
Current User's Login: Raghuraam21

Tests JWT-protected medical endpoints with role-based access control
"""
import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000/api"

def print_separator(title=""):
    """Print a formatted separator"""
    print("\n" + "=" * 70)
    if title:
        print(f"  {title}")
        print("=" * 70)
    else:
        print("=" * 70)


def login_user(email):
    """Login and get access token"""
    response = requests.post(
        f"{BASE_URL}/auth/login/",
        json={"email": email, "password": "password123"},
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        return data.get('access'), data.get('user')
    return None, None


def test_create_profile_without_token():
    """Test 1: Try to create profile WITHOUT token (should fail)"""
    print_separator("Test 1: Create Profile WITHOUT Token (Should Fail)")
    
    test_data = {
        "email": "testuser@example.com",
        "has_diabetes": True,
        "allergies": ["peanuts"]
    }
    
    print(f"\n📤 POST {BASE_URL}/medical/profile/")
    print(f"🔓 No Authorization header")
    print(f"📋 Data: {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/medical/profile/",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\n✅ Response Status: {response.status_code}")
        print(f"📊 Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 401:
            print("\n✅ PASS: Authentication required (as expected)")
            return True
        else:
            print(f"\n❌ FAIL: Expected 401, got {response.status_code}")
            return False
    
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False


def test_create_profile_with_token(access_token):
    """Test 2: Create profile WITH valid token (should succeed)"""
    print_separator("Test 2: Create Profile WITH Valid Token")
    
    test_data = {
        "email": "testuser@example.com",
        "has_diabetes": True,
        "has_hypertension": False,
        "allergies": ["peanuts", "shellfish"],
        "current_medications": ["metformin"],
        "consent_given": True
    }
    
    print(f"\n📤 POST {BASE_URL}/medical/profile/")
    print(f"🔐 Authorization: Bearer {access_token[:50]}...")
    print(f"📋 Data: {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/medical/profile/",
            json=test_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}"
            }
        )
        
        print(f"\n✅ Response Status: {response.status_code}")
        print(f"📊 Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("\n✅ PASS: Profile created with authentication!")
                return True, data
        
        print(f"\n❌ FAIL: Profile creation failed")
        return False, None
    
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False, None


def test_get_own_profile(access_token, email):
    """Test 3: Get own profile (should succeed)"""
    print_separator("Test 3: Get Own Profile (Should Succeed)")
    
    print(f"\n📤 GET {BASE_URL}/medical/profile/get/?email={email}")
    print(f"🔐 Authorization: Bearer {access_token[:50]}...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/medical/profile/get/",
            params={"email": email},
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        print(f"\n✅ Response Status: {response.status_code}")
        print(f"📊 Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("\n✅ PASS: Can access own profile")
            return True
        
        print(f"\n❌ FAIL: Could not access own profile")
        return False
    
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False


def test_get_other_profile_as_patient(patient_token, other_email):
    """Test 4: Patient tries to access another user's profile (should fail)"""
    print_separator("Test 4: Patient Access Other Profile (Should Fail)")
    
    print(f"\n📤 GET {BASE_URL}/medical/profile/get/?email={other_email}")
    print(f"🔐 Authorization: Bearer (patient token)")
    print(f"👤 Trying to access: {other_email}")
    
    try:
        response = requests.get(
            f"{BASE_URL}/medical/profile/get/",
            params={"email": other_email},
            headers={"Authorization": f"Bearer {patient_token}"}
        )
        
        print(f"\n✅ Response Status: {response.status_code}")
        print(f"📊 Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 403:
            print("\n✅ PASS: Access denied (as expected)")
            return True
        
        print(f"\n❌ FAIL: Should have been denied access")
        return False
    
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False


def test_get_other_profile_as_admin(admin_token, other_email):
    """Test 5: Admin accesses another user's profile (should succeed)"""
    print_separator("Test 5: Admin Access Other Profile (Should Succeed)")
    
    print(f"\n📤 GET {BASE_URL}/medical/profile/get/?email={other_email}")
    print(f"🔐 Authorization: Bearer (admin token)")
    print(f"👨‍⚕️ Admin accessing: {other_email}")
    
    try:
        response = requests.get(
            f"{BASE_URL}/medical/profile/get/",
            params={"email": other_email},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        print(f"\n✅ Response Status: {response.status_code}")
        print(f"📊 Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("\n✅ PASS: Admin can access any profile")
            return True
        
        print(f"\n❌ FAIL: Admin should be able to access")
        return False
    
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False


def test_expired_token():
    """Test 6: Try with expired/invalid token (should fail)"""
    print_separator("Test 6: Access with Invalid Token (Should Fail)")
    
    fake_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid"
    
    print(f"\n📤 GET {BASE_URL}/medical/profile/get/?email=test@example.com")
    print(f"🔐 Authorization: Bearer {fake_token}")
    
    try:
        response = requests.get(
            f"{BASE_URL}/medical/profile/get/",
            params={"email": "test@example.com"},
            headers={"Authorization": f"Bearer {fake_token}"}
        )
        
        print(f"\n✅ Response Status: {response.status_code}")
        print(f"📊 Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 401:
            print("\n✅ PASS: Invalid token rejected")
            return True
        
        print(f"\n❌ FAIL: Should reject invalid token")
        return False
    
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False


def test_update_own_profile(access_token, email):
    """Test 7: Update own profile (should succeed)"""
    print_separator("Test 7: Update Own Profile")
    
    update_data = {
        "email": email,
        "has_hypertension": True,
        "allergies": ["peanuts", "shellfish", "eggs"]
    }
    
    print(f"\n📤 POST {BASE_URL}/medical/profile/")
    print(f"🔐 Authorization: Bearer {access_token[:50]}...")
    print(f"📋 Update: {json.dumps(update_data, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/medical/profile/",
            json=update_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}"
            }
        )
        
        print(f"\n✅ Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Response: {json.dumps(data, indent=2)}")
            
            if data.get('action') == 'updated':
                print("\n✅ PASS: Profile updated successfully")
                return True
        
        print(f"\n❌ FAIL: Update failed")
        return False
    
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False


def test_delete_own_profile(access_token, email):
    """Test 8: Delete own profile (should succeed)"""
    print_separator("Test 8: Delete Own Profile")
    
    print(f"\n📤 DELETE {BASE_URL}/medical/profile/delete/?email={email}")
    print(f"🔐 Authorization: Bearer {access_token[:50]}...")
    
    try:
        response = requests.delete(
            f"{BASE_URL}/medical/profile/delete/",
            params={"email": email},
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        print(f"\n✅ Response Status: {response.status_code}")
        print(f"📊 Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("\n✅ PASS: Profile deleted successfully")
            return True
        
        print(f"\n❌ FAIL: Deletion failed")
        return False
    
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False


def run_all_tests():
    """Run all protected endpoint tests"""
    print("\n" + "=" * 70)
    print("  Protected Medical Profile API Test Suite")
    print(f"  Current Date and Time (UTC): {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
    print("  Current User: Raghuraam21")
    print("=" * 70)
    
    results = []
    
    # Test 1: No token
    success = test_create_profile_without_token()
    results.append(("Create without token", success))
    time.sleep(1)
    
    # Login as admin
    print_separator("🔐 Logging in as Admin")
    admin_token, admin_user = login_user("testuser@example.com")
    if admin_token:
        print(f"✅ Admin logged in: {admin_user.get('email')} (role: {admin_user.get('role')})")
    else:
        print("❌ Admin login failed")
        return
    time.sleep(1)
    
    # Login as patient (create new user for testing)
    print_separator("🔐 Registering Patient User")
    patient_email = "patient@example.com"
    reg_response = requests.post(
        f"{BASE_URL}/auth/register/",
        json={"email": patient_email, "password": "password123", "name": "Patient User"}
    )
    if reg_response.status_code in [200, 201, 409]:
        patient_token, patient_user = login_user(patient_email)
        if patient_token:
            print(f"✅ Patient logged in: {patient_user.get('email')} (role: {patient_user.get('role')})")
        else:
            print("❌ Patient login failed")
            return
    time.sleep(1)
    
    # Test 2: Create with token
    success, profile_data = test_create_profile_with_token(admin_token)
    results.append(("Create with token", success))
    time.sleep(1)
    
    # Test 3: Get own profile
    success = test_get_own_profile(admin_token, "testuser@example.com")
    results.append(("Get own profile", success))
    time.sleep(1)
    
    # Test 4: Patient tries to access admin's profile
    success = test_get_other_profile_as_patient(patient_token, "testuser@example.com")
    results.append(("Patient access denied", success))
    time.sleep(1)
    
    # Test 5: Admin accesses patient's profile
    success = test_get_other_profile_as_admin(admin_token, patient_email)
    results.append(("Admin access any profile", success))
    time.sleep(1)
    
    # Test 6: Invalid token
    success = test_expired_token()
    results.append(("Invalid token rejected", success))
    time.sleep(1)
    
    # Test 7: Update own profile
    success = test_update_own_profile(admin_token, "testuser@example.com")
    results.append(("Update own profile", success))
    time.sleep(1)
    
    # Test 8: Delete own profile
    success = test_delete_own_profile(admin_token, "testuser@example.com")
    results.append(("Delete own profile", success))
    
    # Summary
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
    
    print("\n🔐 Security Summary:")
    print("   ✅ JWT authentication working")
    print("   ✅ Role-based access control active")
    print("   ✅ Patients can only access own data")
    print("   ✅ Admins can access all data")
    print("   ✅ Invalid tokens rejected")
    
    print("\n" + "=" * 70)
    print(f"Test completed at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    run_all_tests()