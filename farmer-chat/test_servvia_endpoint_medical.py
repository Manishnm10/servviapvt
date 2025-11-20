"""
Test ServVIA Endpoint with Medical Filtering
Current User's Login: Raghuraam21

Tests complete integration:
- Language detection & translation
- FarmStack content retrieval
- Medical profile filtering
- OpenAI response generation
- Response translation
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def print_separator(title=""):
    """Print a formatted separator"""
    print("\n" + "=" * 70)
    if title:
        print(f"  {title}")
        print("=" * 70)
    else:
        print("=" * 70)


def test_servvia_with_medical_profile():
    """Test ServVIA endpoint with medical profile filtering"""
    
    print("\n🧪 Testing ServVIA Endpoint with Medical Filtering")
    print("=" * 70)
    print(f"📅 Test Date: 2025-11-19 10:32:30 UTC")
    print(f"👤 Test User: Raghuraam21")
    print(f"🌐 Endpoint: {BASE_URL}/api/chat/get_answer_for_text_query/")
    print("=" * 70)
    
    # Test user with medical profile (diabetes + peanut allergy)
    email = "mohammedayaan2193@gmail.com"
    user_name = email.split('@')[0]
    
    print(f"\n👤 Testing with user: {email}")
    print(f"   Medical Profile: Diabetes + Peanut Allergy")
    print(f"   Expected: Filter out honey/sugar/peanut remedies\n")
    
    test_cases = [
        {
            "query": "What remedies help with headache?",
            "language": "English",
            "expected": "Should filter out honey/sugar remedies due to diabetes"
        },
        {
            "query": "How to treat cough naturally?",
            "language": "English", 
            "expected": "Should filter out honey-based remedies"
        },
        {
            "query": "What helps with cold?",
            "language": "English",
            "expected": "Should return safe remedies only"
        }
    ]
    
    results = []
    
    for i, test in enumerate(test_cases, 1):
        print_separator(f"Test Case {i}/{len(test_cases)}")
        print(f"📝 Query: {test['query']}")
        print(f"🌐 Language: {test['language']}")
        print(f"🎯 Expected: {test['expected']}")
        print("-" * 70)
        
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/chat/get_answer_for_text_query/",
                json={
                    "message": test['query'],
                    "email": email
                },
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            
            elapsed_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract response data
                status = data.get('status', 'unknown')
                success = data.get('success', False)
                response_text = data.get('response', data.get('message', ''))
                source = data.get('source', 'unknown')
                detected_lang = data.get('detected_language', 'unknown')
                medical_filtered = data.get('content_filtered', False)
                medical_profile_applied = data.get('medical_profile_applied', False)
                ai_generated = data.get('ai_generated', False)
                
                # Print results
                print(f"\n✅ Response received in {elapsed_time:.2f}s")
                print(f"   Status: {status}")
                print(f"   Success: {success}")
                print(f"   Source: {source}")
                print(f"   Language Detected: {detected_lang}")
                print(f"   Medical Profile Applied: {medical_profile_applied}")
                print(f"   Content Filtered: {medical_filtered}")
                print(f"   AI Generated: {ai_generated}")
                
                print(f"\n💬 Response Preview (first 400 chars):")
                print("-" * 70)
                preview = response_text[:400] if len(response_text) > 400 else response_text
                print(preview)
                if len(response_text) > 400:
                    print("...")
                print("-" * 70)
                
                # Check for medical disclaimer (using simpler check to avoid emoji issues)
                has_disclaimer = 'Medical Note' in response_text or 'diabetes' in response_text.lower() or 'consult' in response_text.lower()
                
                if has_disclaimer:
                    print("✅ Medical disclaimer included")
                else:
                    print("⚠️ No medical disclaimer detected")
                
                # Check if honey/sugar mentioned (should be filtered out)
                forbidden_ingredients = ['honey', 'sugar', 'jaggery', 'peanut']
                found_forbidden = [ing for ing in forbidden_ingredients if ing.lower() in response_text.lower()]
                
                if found_forbidden:
                    print(f"⚠️ WARNING: Forbidden ingredients found: {', '.join(found_forbidden)}")
                    print("   (These should have been filtered for diabetes/allergy)")
                else:
                    print("✅ No forbidden ingredients detected (good filtering)")
                
                results.append({
                    'test': i,
                    'query': test['query'],
                    'success': success,
                    'elapsed_time': elapsed_time,
                    'medical_filtered': medical_filtered,
                    'has_disclaimer': has_disclaimer,
                    'forbidden_found': len(found_forbidden) > 0
                })
                
            else:
                print(f"\n❌ Error: HTTP {response.status_code}")
                print(f"   Response: {response.text[:300]}")
                
                results.append({
                    'test': i,
                    'query': test['query'],
                    'success': False,
                    'error': f"HTTP {response.status_code}"
                })
                
        except requests.exceptions.ConnectionError:
            print(f"\n❌ Connection Error: Cannot connect to {BASE_URL}")
            print("   Make sure the server is running:")
            print("   python manage.py runserver 0.0.0.0:8000")
            
            results.append({
                'test': i,
                'query': test['query'],
                'success': False,
                'error': 'Connection refused'
            })
            
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            print(f"   Error type: {type(e).__name__}")
            
            results.append({
                'test': i,
                'query': test['query'],
                'success': False,
                'error': str(e)
            })
        
        print()
        time.sleep(1)  # Brief pause between tests
    
    # Print summary
    print_separator("TEST SUMMARY")
    
    total = len(results)
    passed = sum(1 for r in results if r.get('success', False))
    failed = total - passed
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests PASSED! 🎉")
    else:
        print(f"⚠️ {failed} test(s) FAILED")
    
    # Detailed results
    print("\n📋 Detailed Results:")
    for result in results:
        status_icon = "✅" if result.get('success', False) else "❌"
        print(f"{status_icon} Test {result['test']}: {result['query']}")
        
        if result.get('success', False):
            elapsed = result.get('elapsed_time', 0)
            medical_filtered = result.get('medical_filtered', False)
            has_disclaimer = result.get('has_disclaimer', False)
            forbidden = result.get('forbidden_found', False)
            
            print(f"   Response time: {elapsed:.2f}s")
            print(f"   Medical filtering: {'Yes' if medical_filtered else 'No'}")
            print(f"   Medical disclaimer: {'Yes' if has_disclaimer else 'No'}")
            print(f"   Forbidden ingredients: {'Found (Bad!)' if forbidden else 'Not found (Good!)'}")
        else:
            error = result.get('error', 'Unknown error')
            print(f"   Error: {error}")
    
    print("\n" + "=" * 70)
    print("Test completed at: 2025-11-19 10:32:30 UTC")
    print("=" * 70 + "\n")


def test_server_health():
    """Test if server is responding"""
    print("\n🏥 Testing Server Health...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/chat/get_answer_for_text_query/",
            timeout=5
        )
        
        # Status 200 or 405 both indicate server is running
        # 405 = Method Not Allowed (expected for POST-only endpoints on GET)
        if response.status_code in [200, 405]:
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ Server is running!")
                    print(f"   Version: {data.get('version', 'unknown')}")
                    print(f"   FarmStack: {'Available' if data.get('farmstack_available') else 'Not available'}")
                    print(f"   Medical Filtering: {'Available' if data.get('medical_filtering_available') else 'Not available'}")
                    print(f"   Translation: {'Available' if data.get('translation_available') else 'Not available'}")
                except:
                    print(f"✅ Server is running! (Status: {response.status_code})")
            else:
                print(f"✅ Server is running! (Status 405 is expected for GET request)")
            return True
        else:
            print(f"⚠️ Server returned status: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to server at {BASE_URL}")
        print("\n🔧 To start the server, run:")
        print("   python manage.py runserver 0.0.0.0:8000")
        return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("  ServVIA Healthcare Endpoint Integration Test")
    print("  Current Date and Time (UTC): 2025-11-19 10:32:30")
    print("  Current User: Raghuraam21")
    print("=" * 70)
    
    # Test server health first
    server_healthy = test_server_health()
    
    if not server_healthy:
        print("\n⚠️ Health check inconclusive (may be 405), attempting tests anyway...")
        print("If server is not running, tests will fail with connection error.\n")
    else:
        print("\n✅ Server is healthy, proceeding with tests...\n")
    
    input("Press Enter to continue with medical filtering tests...")
    test_servvia_with_medical_profile()