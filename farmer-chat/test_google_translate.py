import os
import sys
import django

# Set up paths and Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_core.settings')

# Set Google credentials explicitly
credentials_path = os.path.join(os.getcwd(), 'credentials', 'google-translate-key.json')
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path

django.setup()

def test_google_translation():
    print("🌐 Testing Google Translation API Setup...")
    print(f"📁 Credentials path: {credentials_path}")
    print(f"📄 Credentials file exists: {os.path.exists(credentials_path)}")
    
    try:
        from google.cloud import translate_v2 as translate
        
        # Initialize the client
        translate_client = translate.Client()
        print("✅ Google Translate client initialized successfully")
        
        # Test basic translation
        test_texts = [
            "I have cough",
            "Tengo tos",  # Spanish
            "J'ai une toux",  # French
        ]
        
        for text in test_texts:
            try:
                # Detect language
                detection = translate_client.detect_language(text)
                detected_lang = detection['language']
                confidence = detection['confidence']
                
                # Translate to English if not already English
                if detected_lang != 'en':
                    result = translate_client.translate(text, target_language='en')
                    translated = result['translatedText']
                else:
                    translated = text
                
                print(f"📝 Original: '{text}'")
                print(f"🔍 Detected: {detected_lang} (confidence: {confidence})")
                print(f"🌐 Translated: '{translated}'")
                print("---")
                
            except Exception as text_error:
                print(f"❌ Error translating '{text}': {text_error}")
        
        return True
        
    except Exception as e:
        print(f"❌ Google Translation Test Failed: {e}")
        print("\n💡 Troubleshooting:")
        print("1. Make sure your Google Cloud project has Translation API enabled")
        print("2. Check that the service account has proper permissions")
        print("3. Verify the JSON credentials file is valid")
        return False

if __name__ == "__main__":
    success = test_google_translation()
    
    if success:
        print("\n🎉 Google Translation is working correctly!")
        print("✅ ServVIA is ready for multi-language healthcare support!")
    else:
        print("\n⚠️ Google Translation setup needs attention")
    
    input("\nPress Enter to continue...")