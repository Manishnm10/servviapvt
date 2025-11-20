"""
JWT Authentication Test Suite
Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): 2025-11-19 12:11:46
Current User's Login: Raghuraam21

Tests authentication flow:
- User registration
- User login
- Token verification
- Token refresh
- Logout
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


def test_register():
    """Test user registration"""
    print_separator("Test 1: User Registration")
    
    test_data = {
        "email": "testuser@example.com",
        "password": "SecurePass123!",
        "name": "Test User"
    }
    
    print(f"\n📤 Sending POST request to {BASE_URL}/auth/register/")
    print(f"📋 Data:")
    print(json.dumps(test_data, indent=2))
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register/",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"\n✅ Response Status: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"\n📊 Response Data:")
            print(json.dumps(data, indent=2))
            
            if data.get('success'):
                print("\n✅ PASS: User registered successfully!")
                print(f"   User ID: {data.get('user', {}).get('id')}")
                print(f"   Email: {data.get('user', {}).get('email')}")
                print(f"   Access Token: {data.get('access')[:50]}...")
                print(f"   Refresh Token: {data.get('refresh')[:50]}...")
                return True, data
            else:
                print(f"\n❌ FAIL: {data.get('error', 'Unknown error')}")
                return False, None
        elif response.status_code == 409:
            print(f"\n⚠️ User already exists (expected if running tests multiple times)")
            # Try login instead
            return test_login()
        else:
            print(f"\n❌ FAIL: HTTP {response.status_code}")
            print(f"Response: {response.text[:300]}")
            return False, None
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False, None


def test_login():
    """Test user login"""
    print_separator("Test 2: User Login")
    
    test_data = {
        "email": "testuser@example.com",
        "password": "SecurePass123!"
    }
    
    print(f"\n📤 Sending POST request to {BASE_URL}/auth/login/")
    print(f"📋 Data:")
    print(json.dumps(test_data, indent=2))
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login/",
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
                print("\n✅ PASS: User logged in successfully!")
                print(f"   User ID: {data.get('user', {}).get('id')}")
                print(f"   Email: {data.get('user', {}).get('email')}")
                print(f"   Access Token: {data.get('access')[:50]}...")
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


def test_verify_token(access_token):
    """Test token verification"""
    print_separator("Test 3: Verify Token")
    
    test_data = {
        "token": access_token
    }
    
    print(f"\n📤 Sending POST request to {BASE_URL}/auth/token/verify/")
    print(f"📋 Token: {access_token[:50]}...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/token/verify/",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"\n✅ Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n📊 Response Data:")
            print(json.dumps(data, indent=2))
            
            if data.get('valid'):
                print("\n✅ PASS: Token is valid!")
                return True, data
            else:
                print(f"\n❌ FAIL: Token is invalid")
                return False, None
        else:
            print(f"\n❌ FAIL: HTTP {response.status_code}")
            return False, None
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False, None


def test_protected_endpoint(access_token):
    """Test accessing medical profile with token"""
    print_separator("Test 4: Access Protected Endpoint (Medical Profile)")
    
    email = "testuser@example.com"
    
    print(f"\n📤 Sending GET request to {BASE_URL}/medical/profile/get/")
    print(f"📋 Email: {email}")
    print(f"🔐 Authorization: Bearer {access_token[:50]}...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/medical/profile/get/",
            params={"email": email},
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10
        )
        
        print(f"\n✅ Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n📊 Response Data:")
            print(json.dumps(data, indent=2))
            
            print("\n✅ PASS: Protected endpoint accessible with valid token!")
            return True, data
        else:
            print(f"\n❌ FAIL: HTTP {response.status_code}")
            return False, None
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False, None


def test_refresh_token(refresh_token):
    """Test refreshing access token"""
    print_separator("Test 5: Refresh Access Token")
    
    test_data = {
        "refresh": refresh_token
    }
    
    print(f"\n📤 Sending POST request to {BASE_URL}/auth/token/refresh/")
    print(f"📋 Refresh Token: {refresh_token[:50]}...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/token/refresh/",
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
                print("\n✅ PASS: Token refreshed successfully!")
                print(f"   New Access Token: {data.get('access')[:50]}...")
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


def test_logout(refresh_token):
    """Test user logout"""
    print_separator("Test 6: User Logout")
    
    test_data = {
        "refresh": refresh_token
    }
    
    print(f"\n📤 Sending POST request to {BASE_URL}/auth/logout/")
    print(f"📋 Refresh Token: {refresh_token[:50]}...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/logout/",
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
                print("\n✅ PASS: User logged out successfully!")
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
    """Run all authentication tests"""
    print("\n" + "="*70)
    print("  JWT Authentication Test Suite")
    print("  Current Date and Time (UTC): 2025-11-19 12:11:46")
    print("  Current User: Raghuraam21")
    print("="*70)
    
    results = []
    tokens = {}
    
    # Test 1: Register (or login if exists)
    success, data = test_register()
    results.append(("Register/Login", success))
    if success and data:
        tokens['access'] = data.get('access')
        tokens['refresh'] = data.get('refresh')
    time.sleep(1)
    
    # Test 2: Verify token
    if tokens.get('access'):
        success, data = test_verify_token(tokens['access'])
        results.append(("Verify Token", success))
        time.sleep(1)
    
    # Test 3: Access protected endpoint
    if tokens.get('access'):
        success, data = test_protected_endpoint(tokens['access'])
        results.append(("Access Protected Endpoint", success))
        time.sleep(1)
    
    # Test 4: Refresh token
    if tokens.get('refresh'):
        success, data = test_refresh_token(tokens['refresh'])
        results.append(("Refresh Token", success))
        if success and data:
            tokens['new_access'] = data.get('access')
        time.sleep(1)
    
    # Test 5: Logout
    if tokens.get('refresh'):
        success, data = test_logout(tokens['refresh'])
        results.append(("Logout", success))
    
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
    print("Test completed at: 2025-11-19 12:11:46 UTC")
    print("="*70 + "\n")


if __name__ == "__main__":
    run_all_tests()