import os, sys, django
sys.path.append('.')

# Set Google credentials
credentials_path = os.path.join(os.getcwd(), 'credentials', 'google-translate-key.json')
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_core.settings')

django.setup()

def debug_translation():
    try:
        from language_service.translation import detect_language_and_translate_to_english
        from healthcare.pdf_content_handler import get_healthcare_response_from_pdf
        import asyncio
        
        test_queries = [
            "I have cough",
            "Tengo tos", 
            "J'ai une toux",
            "I have a cough",
            "I am coughing"
        ]
        
        for query in test_queries:
            print(f"\n--- Testing: '{query}' ---")
            
            # Get translation
            english_query, detected_lang = asyncio.run(detect_language_and_translate_to_english(query))
            print(f"Detected language: {detected_lang}")
            print(f"English translation: '{english_query}'")
            
            # Test PDF search
            response = get_healthcare_response_from_pdf(english_query, 'TestUser')
            
            if "here's what I found" in response:
                print("✅ Found remedies in PDF")
            else:
                print("❌ No remedies found - using fallback")
            
            print("---")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_translation()
    input("Press Enter to continue...")