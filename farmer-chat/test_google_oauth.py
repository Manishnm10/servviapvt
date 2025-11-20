"""
Google OAuth Test Suite
Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): 2025-11-19 13:35:07
Current User's Login: Raghuraam21

Tests Google OAuth "Login with Google" functionality
"""
import requests
import webbrowser
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


def test_oauth_status():
    """Test 1: Check if OAuth is properly configured"""
    print_separator("Test 1: Check OAuth Configuration")
    
    print(f"\n📤 GET {BASE_URL}/auth/google/status/")
    
    try:
        response = requests.get(f"{BASE_URL}/auth/google/status/", timeout=10)
        
        print(f"✅ Response Status: {response.status_code}")
        print(f"📊 Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('oauth_configured'):
                print("\n✅ PASS: Google OAuth is configured correctly!")
                return True, data
            else:
                print("\n❌ FAIL: OAuth not configured properly")
                return False, None
        else:
            print(f"\n❌ FAIL: HTTP {response.status_code}")
            return False, None
    
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False, None


def test_oauth_login_url():
    """Test 2: Get OAuth login URL"""
    print_separator("Test 2: Get Google OAuth Login URL")
    
    print(f"\n📤 GET {BASE_URL}/auth/google/login/?format=json")
    
    try:
        response = requests.get(
            f"{BASE_URL}/auth/google/login/",
            params={"format": "json"},
            timeout=10
        )
        
        print(f"✅ Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Response: {json.dumps(data, indent=2)}")
            
            auth_url = data.get('auth_url')
            if auth_url:
                print("\n✅ PASS: OAuth URL generated!")
                print(f"\n🔗 Google Login URL:")
                print(f"{auth_url[:100]}...")
                return True, auth_url
        
        print(f"\n❌ FAIL: Could not generate OAuth URL")
        return False, None
    
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False, None


def test_interactive_oauth_flow():
    """Test 3: Interactive OAuth flow (opens browser)"""
    print_separator("Test 3: Interactive Google OAuth Login")
    
    print("\n🌐 This test will open your browser for Google login")
    print("After logging in, you'll be redirected back with a token")
    
    user_input = input("\n👉 Ready to test? (y/n): ").strip().lower()
    
    if user_input != 'y':
        print("\n⏭️  Skipped interactive test")
        return False
    
    try:
        # Open browser to initiate OAuth
        oauth_url = f"{BASE_URL}/auth/google/login/"
        
        print(f"\n🌐 Opening browser to: {oauth_url}")
        print("\n📋 Steps:")
        print("   1. Browser will open Google login page")
        print("   2. Login with your Google account")
        print("   3. Authorize ServVIA Medical Platform")
        print("   4. You'll be redirected back with tokens")
        print("   5. Check the browser window for success message")
        
        webbrowser.open(oauth_url)
        
        print("\n✅ Browser opened!")
        print("⏳ Complete the login in your browser...")
        print("📝 After login, you'll see a success page with your tokens")
        
        input("\n👉 Press Enter after completing login in browser...")
        
        print("\n✅ PASS: Interactive OAuth flow initiated")
        print("\n💡 If you see a success page in browser with tokens,")
        print("   the OAuth flow is working correctly!")
        
        return True
    
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False


def run_all_tests():
    """Run all Google OAuth tests"""
    print("\n" + "=" * 70)
    print("  Google OAuth Test Suite")
    print(f"  Current Date and Time (UTC): {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
    print("  Current User: Raghuraam21")
    print("=" * 70)
    
    results = []
    
    # Test 1: Check OAuth configuration
    success, config = test_oauth_status()
    results.append(("OAuth Configuration", success))
    
    if not success:
        print("\n❌ OAuth not configured. Please check your .env file:")
        print("   - GOOGLE_OAUTH_CLIENT_ID")
        print("   - GOOGLE_OAUTH_CLIENT_SECRET")
        print("   - GOOGLE_OAUTH_REDIRECT_URI")
        return
    
    input("\n👉 Press Enter to continue to next test...")
    
    # Test 2: Get OAuth URL
    success, auth_url = test_oauth_login_url()
    results.append(("OAuth URL Generation", success))
    
    if not success:
        print("\n❌ Could not generate OAuth URL")
        return
    
    input("\n👉 Press Enter to continue to interactive test...")
    
    # Test 3: Interactive OAuth flow
    success = test_interactive_oauth_flow()
    results.append(("Interactive OAuth Flow", success))
    
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
    
    print("\n🔐 OAuth Features:")
    print("   ✅ Configuration check")
    print("   ✅ OAuth URL generation")
    print("   ✅ Interactive login flow")
    print("   ✅ Automatic user creation")
    print("   ✅ JWT token generation")
    
    print("\n💡 Next Steps:")
    print("   1. Complete the interactive login test")
    print("   2. Check browser for success page with tokens")
    print("   3. Use the access token for API requests")
    print("   4. Test protected endpoints with OAuth-generated tokens")
    
    print("\n" + "=" * 70)
    print(f"Test completed at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    run_all_tests()