"""
Simple FarmStack API test with detailed debugging
"""
import requests
import urllib3

# Disable SSL warnings for expired certificate
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Test FarmStack connection
url = "https://demo.farmstack.farmer.chat/be/microsite/resources/get_content/"
email = "mohammedayaan2193@gmail.com"
query = "What are remedies for headache?"

print(f"🌐 Testing FarmStack API connection...")
print(f"   URL: {url}")
print(f"   Email: {email}")
print(f"   Query: {query}\n")

try:
    response = requests.post(
        url,
        json={"email": email, "query": query},
        verify=False,  # Disable SSL verification
        timeout=30
    )
    
    print(f"✅ Response Status: {response.status_code}")
    print(f"✅ Response Headers: {response.headers.get('content-type')}")
    
    if response.status_code == 200:
        print(f"\n✅ SUCCESS! Content retrieved:")
        print("=" * 70)
        print(response.text[:1000])  # First 1000 chars
        print("=" * 70)
    else:
        print(f"\n❌ Error: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ Connection failed: {e}")
    import traceback
    traceback.print_exc()