import os, sys, django
sys.path.append('.')

# Set Google credentials
credentials_path = os.path.join(os.getcwd(), 'credentials', 'google-translate-key.json')
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_core.settings')

django.setup()

def test_servvia_with_translation():
    try:
        from api.utils import process_query
        from healthcare.pdf_content_handler import get_healthcare_response_from_pdf
        
        print("🏥 Testing ServVIA with Google Translation...")
        
        # Test cases in different languages
        test_cases = [
            {"query": "I have cough", "language": "English"},
            {"query": "Tengo tos", "language": "Spanish"}, 
            {"query": "J'ai une toux", "language": "French"},
        ]
        
        for test_case in test_cases:
            print(f"\n--- Testing {test_case['language']} ---")
            print(f"Query: {test_case['query']}")
            
            try:
                result = process_query(
                    test_case['query'], 
                    'manishnm10@test.com', 
                    {'first_name': 'Manish'}
                )
                
                response = result.get('translated_response', 'No response')
                print(f"Response preview: {response[:150]}...")
                print(f"Source: {result.get('source', 'No source')}")
                print("✅ Test passed")
                
            except Exception as e:
                print(f"❌ Test failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ ServVIA translation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_servvia_with_translation()
    input("\nPress Enter to continue...")