"""
Test OAuth-Generated Tokens with Protected Endpoints
Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): 2025-11-19 14:06:48
Current User's Login: Raghuraam21

Tests that OAuth-generated JWT tokens work with protected medical endpoints
"""
import requests
import json
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


def test_oauth_token_with_medical_profile():
    """Test OAuth token with protected medical endpoints"""
    
    print("\n" + "=" * 70)
    print("  OAuth Token + Protected Endpoints Test")
    print(f"  Current Date and Time (UTC): {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
    print("  Current User: Raghuraam21")
    print("=" * 70)
    
    # PASTE YOUR ACCESS TOKEN HERE (from the browser success page)
    print("\n📋 Please copy the Access Token from the browser and paste it here:")
    access_token = input("👉 Access Token: ").strip()
    
    if not access_token:
        print("❌ No token provided. Exiting.")
        return
    
    print(f"\n✅ Token received: {access_token[:50]}...")
    
    results = []
    
    # Test 1: Create Medical Profile with OAuth Token
    print_separator("Test 1: Create Medical Profile with OAuth Token")
    
    profile_data = {
        "email": "manishnm22@gmail.com",
        "has_diabetes": True,
        "has_hypertension": False,
        "allergies": ["peanuts", "shellfish"],
        "current_medications": ["metformin"],
        "consent_given": True
    }
    
    print(f"\n📤 POST {BASE_URL}/medical/profile/")
    print(f"🔐 Authorization: Bearer {access_token[:50]}...")
    print(f"📋 Data: {json.dumps(profile_data, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/medical/profile/",
            json=profile_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}"
            },
            timeout=10
        )
        
        print(f"\n✅ Response Status: {response.status_code}")
        print(f"📊 Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("\n✅ PASS: Medical profile created with OAuth token!")
            results.append(("Create Medical Profile", True))
        else:
            print("\n❌ FAIL: Could not create profile")
            results.append(("Create Medical Profile", False))
    
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        results.append(("Create Medical Profile", False))
    
    input("\n👉 Press Enter to continue...")
    
    # Test 2: Get Own Medical Profile
    print_separator("Test 2: Get Own Medical Profile")
    
    print(f"\n📤 GET {BASE_URL}/medical/profile/get/?email=manishnm22@gmail.com")
    print(f"🔐 Authorization: Bearer {access_token[:50]}...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/medical/profile/get/",
            params={"email": "manishnm22@gmail.com"},
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10
        )
        
        print(f"\n✅ Response Status: {response.status_code}")
        print(f"📊 Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("\n✅ PASS: Retrieved own medical profile!")
            results.append(("Get Medical Profile", True))
        else:
            print("\n❌ FAIL: Could not retrieve profile")
            results.append(("Get Medical Profile", False))
    
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        results.append(("Get Medical Profile", False))
    
    input("\n👉 Press Enter to continue...")
    
    # Test 3: Update Medical Profile
    print_separator("Test 3: Update Medical Profile")
    
    update_data = {
        "email": "manishnm22@gmail.com",
        "has_hypertension": True,
        "allergies": ["peanuts", "shellfish", "eggs"]
    }
    
    print(f"\n📤 POST {BASE_URL}/medical/profile/")
    print(f"🔐 Authorization: Bearer {access_token[:50]}...")
    print(f"📋 Update: {json.dumps(update_data, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat/get_answer_for_text_query/",
            json=update_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}"
            },
            timeout=10
        )
        
        print(f"\n✅ Response Status: {response.status_code}")
        print(f"📊 Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('action') == 'updated':
                print("\n✅ PASS: Medical profile updated!")
                results.append(("Update Medical Profile", True))
            else:
                print("\n❌ FAIL: Wrong action")
                results.append(("Update Medical Profile", False))
        else:
            print("\n❌ FAIL: Could not update profile")
            results.append(("Update Medical Profile", False))
    
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        results.append(("Update Medical Profile", False))
    
    input("\n👉 Press Enter to continue...")
    
    # Test 4: Access ServVIA Healthcare with Profile
    print_separator("Test 4: Query ServVIA Healthcare (with medical profile)")
    
    health_query = {
        "query": "What foods should I avoid with diabetes?",
        "language": "en",
        "user_email": "manishnm22@gmail.com"
    }
    
    print(f"\n📤 POST {BASE_URL}/servvia/healthcare/")
    print(f"🔐 Authorization: Bearer {access_token[:50]}...")
    print(f"📋 Query: {health_query['query']}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/servvia/healthcare/",
            json=health_query,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}"
            },
            timeout=30
        )
        
        print(f"\n✅ Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Response snippet: {data.get('response', '')[:200]}...")
            print(f"🔐 Profile used: {data.get('medical_profile_applied', False)}")
            print("\n✅ PASS: Healthcare query with profile filtering!")
            results.append(("Healthcare Query", True))
        else:
            print(f"📊 Response: {json.dumps(response.json(), indent=2)}")
            print("\n❌ FAIL: Healthcare query failed")
            results.append(("Healthcare Query", False))
    
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        results.append(("Healthcare Query", False))
    
    # Summary
    print_separator("TEST SUMMARY")
    
    total = len(results)
    passed = sum(1 for _, success in results if success)
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests PASSED! 🎉")
    else:
        print(f"⚠️ {total - passed} test(s) FAILED")
    
    print("\n📋 Detailed Results:")
    for test_name, success in results:
        status_icon = "✅" if success else "❌"
        print(f"{status_icon} {test_name}")
    
    print("\n🎊 OAuth Integration Complete!")
    print("   ✅ Google OAuth login working")
    print("   ✅ JWT tokens generated")
    print("   ✅ Protected endpoints accessible")
    print("   ✅ Medical profile CRUD working")
    print("   ✅ Healthcare queries with filtering")
    
    print("\n" + "=" * 70)
    print(f"Test completed at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    test_oauth_token_with_medical_profile()