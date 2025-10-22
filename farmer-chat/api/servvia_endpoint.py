from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import logging
import asyncio

logger = logging.getLogger(__name__)

try:
    from healthcare.pdf_content_handler import get_healthcare_response_from_pdf
    HEALTHCARE_PDF_AVAILABLE = True
    print("✅ ServVIA Healthcare PDF handler loaded successfully")
except ImportError as e:
    HEALTHCARE_PDF_AVAILABLE = False
    print(f"❌ ServVIA Healthcare PDF handler not available: {e}")

# Import translation service
try:
    from language_service.translation import detect_language_and_translate_to_english, translate_text_to_language
    TRANSLATION_AVAILABLE = True
    print("✅ ServVIA Translation service loaded successfully")
except ImportError as e:
    TRANSLATION_AVAILABLE = False
    print(f"❌ ServVIA Translation service not available: {e}")

@csrf_exempt
def get_answer_for_text_query(request):
    """
    ServVIA Healthcare endpoint with automatic language detection and response
    """
    
    # Handle GET request (for testing)
    if request.method == "GET":
        return JsonResponse({
            "message": "ServVIA Healthcare Endpoint with Auto Language Detection is Ready! 🌐🏥",
            "pdf_available": HEALTHCARE_PDF_AVAILABLE,
            "translation_available": TRANSLATION_AVAILABLE,
            "features": [
                "Automatic language detection",
                "Healthcare remedies from PDF", 
                "Response in user's language"
            ],
            "instructions": "Send POST request with {'message': 'your health query', 'email': 'your@email.com'}",
            "status": "success"
        })
    
    # Handle POST request
    if request.method == "POST":
        try:
            # Parse POST request data
            if request.content_type == 'application/json':
                data = json.loads(request.body) if request.body else {}
            else:
                data = dict(request.POST)
            
            # Extract query and email from request
            original_query = data.get('message', data.get('query', data.get('text', '')))
            email = data.get('email', data.get('userEmail', 'user@servvia.com'))
            
            # Handle list values (from form data)
            if isinstance(original_query, list):
                original_query = original_query[0] if original_query else ''
            if isinstance(email, list):
                email = email[0] if email else 'user@servvia.com'
            
            user_name = email.split('@')[0] if '@' in str(email) else 'User'
            
            print(f"🌐 ServVIA: Processing '{original_query}' for {user_name}")
            logger.info(f"🌐 ServVIA: Processing '{original_query}' for {user_name}")
            
            if not original_query or not str(original_query).strip():
                return JsonResponse({
                    "success": True,
                    "message": f"Hello {user_name}! Please ask me a health-related question, and I'll help you with remedies and guidance in your language. 🏥🌐",
                    "response": f"Hello {user_name}! Please ask me a health-related question, and I'll help you with remedies and guidance in your language. 🏥🌐",
                    "user": user_name,
                    "status": "success"
                })

            # Step 1: Detect user's language and translate to English for processing
            detected_language = "en"  # Default
            english_query = str(original_query)
            
            if TRANSLATION_AVAILABLE:
                try:
                    print("🌐 ServVIA: Detecting language and translating...")
                    english_query, detected_language = asyncio.run(
                        detect_language_and_translate_to_english(str(original_query))
                    )
                    print(f"✅ ServVIA: Detected '{detected_language}' | Translated: '{english_query}'")
                except Exception as trans_error:
                    print(f"⚠️ ServVIA: Translation detection failed, using original: {trans_error}")
                    english_query = str(original_query)
                    detected_language = "en"
            
            # Step 2: Generate healthcare response from PDF (in English)
            healthcare_response_english = ""
            
            if HEALTHCARE_PDF_AVAILABLE:
                try:
                    print("🏥 ServVIA: Generating healthcare response from PDF...")
                    healthcare_response_english = get_healthcare_response_from_pdf(english_query, user_name)
                    print(f"✅ ServVIA: Healthcare response generated")
                except Exception as pdf_error:
                    print(f"❌ ServVIA PDF Error: {pdf_error}")
                    healthcare_response_english = f"Hello {user_name}! I understand you're asking about '{original_query}'. For your health and safety, please consult a healthcare professional for specific medical advice. 🏥"
            else:
                healthcare_response_english = f"Hello {user_name}! I understand you're asking about '{original_query}'. For your health and safety, please consult a healthcare professional for specific medical advice. 🏥"
            
            # Step 3: Translate response back to user's detected language
            final_response = healthcare_response_english
            
            # FIX: Always translate back if not English (handle all non-English languages)
            if TRANSLATION_AVAILABLE and detected_language and detected_language.lower() != "en":
                try:
                    print(f"🌐 ServVIA: Translating response to '{detected_language}'...")
                    final_response = asyncio.run(
                        translate_text_to_language(healthcare_response_english, detected_language)
                    )
                    print(f"✅ ServVIA: Response translated successfully to {detected_language}")
                except Exception as trans_error:
                    print(f"⚠️ ServVIA: Response translation failed: {trans_error}")
                    final_response = healthcare_response_english
            else:
                print(f"ℹ️ ServVIA: Keeping response in English (detected: {detected_language})")
            
            response_data = {
                "success": True,
                "message": final_response,
                "response": final_response,
                "source": "Home_Remedies_Guide.pdf" if HEALTHCARE_PDF_AVAILABLE else None,
                "user": user_name,
                "detected_language": detected_language,
                "original_query": str(original_query),
                "english_query": english_query,
                "language_auto_detected": True,
                "status": "success"
            }
            
            print(f"✅ ServVIA: Complete multilingual response generated for {user_name}")
            return JsonResponse(response_data)
                
        except Exception as e:
            print(f"❌ ServVIA Endpoint Error: {e}")
            logger.error(f"ServVIA Endpoint Error: {e}")
            return JsonResponse({
                "success": False,
                "message": "I'm experiencing technical difficulties. Please consult a healthcare professional for medical advice.",
                "error": str(e),
                "status": "error"
            }, status=500)
    
    # Handle other methods
    return JsonResponse({
        "error": "Method not allowed",
        "allowed_methods": ["GET", "POST"]
    }, status=405)
