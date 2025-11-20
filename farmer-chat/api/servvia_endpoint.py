"""
ServVIA Healthcare Endpoint
Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): 2025-11-20 12:30:15
Current User's Login: Raghuraam21

Integrates with FarmStack API for content retrieval
Filters remedies based on user's medical profile
Supports multilingual queries and responses
Uses OpenAI for natural language response generation
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import logging
import asyncio
import re

logger = logging.getLogger(__name__)

# Import FarmStack content retrieval
try:
    from retrieval.content_retrieval import retrieve_content_from_api
    FARMSTACK_AVAILABLE = True
    print("✅ ServVIA FarmStack integration loaded successfully")
except ImportError as e:
    FARMSTACK_AVAILABLE = False
    print(f"❌ ServVIA FarmStack integration not available: {e}")

# Import generation handler (uses existing OpenAI-based generation)
try:
    from generation.generate_response import generate_query_response
    GENERATION_AVAILABLE = True
    print("✅ ServVIA Response generation loaded successfully")
except ImportError as e:
    GENERATION_AVAILABLE = False
    print(f"❌ ServVIA Response generation not available: {e}")

# Import medical profile filtering
try:
    from medical.remedy_filter import filter_remedies_by_medical_profile
    from medical.medical_db_operations import get_medical_profile_by_user_id
    MEDICAL_FILTERING_AVAILABLE = True
    print("✅ ServVIA Medical filtering loaded successfully")
except ImportError as e:
    MEDICAL_FILTERING_AVAILABLE = False
    print(f"❌ ServVIA Medical filtering not available: {e}")

# Import translation service
try:
    from language_service.translation import detect_language_and_translate_to_english, translate_text_to_language
    TRANSLATION_AVAILABLE = True
    print("✅ ServVIA Translation service loaded successfully")
except ImportError as e:
    TRANSLATION_AVAILABLE = False
    print(f"❌ ServVIA Translation service not available: {e}")

# Import User model for ID lookup
try:
    from database.models import User
    USER_MODEL_AVAILABLE = True
except ImportError as e:
    USER_MODEL_AVAILABLE = False
    print(f"⚠️ User model not available: {e}")


def clean_ai_response_formatting(text):
    """
    Remove bullets and numbers from AI-generated response.
    Let the frontend handle list formatting using markdown.
    """
    if not text or not isinstance(text, str):
        return text
    
    # Remove bullet points at start of lines
    text = re.sub(r'^[•●○]\s*', '', text, flags=re.MULTILINE)
    
    # Remove numbered lists at start of lines (1. 2. 3. etc)
    text = re.sub(r'^\d+\.\s*', '', text, flags=re.MULTILINE)
    
    return text


@csrf_exempt
@require_http_methods(["GET", "POST", "OPTIONS"])
def get_answer_for_text_query(request):
    """
    ServVIA Healthcare endpoint with:
    - Automatic language detection and translation
    - FarmStack API content retrieval
    - Medical profile-based filtering
    - OpenAI-powered response generation
    - Personalized health recommendations
    
    Current Date and Time (UTC): 2025-11-20 12:30:15
    Current User: Raghuraam21
    """
    
    # Handle OPTIONS request (CORS preflight)
    if request.method == "OPTIONS":
        response = JsonResponse({"status": "ok"})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response
    
    # Handle GET request (for testing)
    if request.method == "GET":
        return JsonResponse({
            "message": "ServVIA Healthcare Endpoint is Ready! 🌐🏥",
            "version": "2.0 - FarmStack Integration",
            "farmstack_available": FARMSTACK_AVAILABLE,
            "medical_filtering_available": MEDICAL_FILTERING_AVAILABLE,
            "translation_available": TRANSLATION_AVAILABLE,
            "generation_available": GENERATION_AVAILABLE,
            "features": [
                "Automatic language detection",
                "FarmStack content retrieval", 
                "Medical profile filtering",
                "OpenAI-powered response generation",
                "Personalized health recommendations",
                "Response in user's language"
            ],
            "instructions": "Send POST request with {'query': 'your health query', 'email': 'your@email.com'}",
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
            
            # ✅ FIXED: Extract query and email properly
            original_query = data.get('query') or data.get('message') or data.get('text', '')
            user_email = data.get('email', '')
            
            # Handle list values (from form data)
            if isinstance(original_query, list):
                original_query = original_query[0] if original_query else ''
            if isinstance(user_email, list):
                user_email = user_email[0] if user_email else ''
            
            # ✅ FIXED: Validate email is provided
            if not user_email or not str(user_email).strip():
                logger.error("❌ No user email provided in request")
                return JsonResponse({
                    "success": False,
                    "error": "Email is required for personalized healthcare assistance"
                }, status=400)
            
            # Clean and validate
            user_email = str(user_email).strip()
            original_query = str(original_query).strip()
            
            # ✅ FIXED: Get user's actual name from database
            user_name = 'User'  # Default
            if USER_MODEL_AVAILABLE:
                try:
                    user = User.get(User.email == user_email)
                    # Use first_name + last_name if available
                    if hasattr(user, 'first_name') and user.first_name:
                        user_name = user.first_name
                        if hasattr(user, 'last_name') and user.last_name:
                            user_name = f"{user.first_name} {user.last_name}"
                        print(f"✅ User name loaded: {user_name}")
                    else:
                        # Fallback to email username
                        user_name = user_email.split('@')[0]
                        print(f"ℹ️ Using email username: {user_name}")
                except Exception as e:
                    print(f"⚠️ Could not get user name: {e}")
                    user_name = user_email.split('@')[0]
            else:
                # Fallback if User model not available
                user_name = user_email.split('@')[0]
            
            print(f"🌐 ServVIA: Processing '{original_query}' for {user_email}")
            logger.info(f"🌐 ServVIA: Processing '{original_query}' for {user_email}")
            
            # Validate query
            if not original_query:
                return JsonResponse({
                    "success": True,
                    "answer": "Hello! 🏥 Please ask me a health-related question, and I'll help you with remedies and guidance in your language. 🌐",
                    "response": "Hello! 🏥 Please ask me a health-related question, and I'll help you with remedies and guidance in your language. 🌐",
                    "user": user_name,
                    "status": "success"
                })

            # ============================================================
            # STEP 1: Detect user's language and translate to English
            # ============================================================
            detected_language = "en"  # Default
            english_query = original_query
            
            if TRANSLATION_AVAILABLE:
                try:
                    print("🌐 ServVIA: Detecting language and translating...")
                    english_query, detected_language = asyncio.run(
                        detect_language_and_translate_to_english(original_query)
                    )
                    print(f"✅ ServVIA: Detected '{detected_language}' | Translated: '{english_query}'")
                    
                    # ✅ Enhanced translation for non-English queries
                    if detected_language.lower() != 'en':
                        print(f"📝 Original query: '{original_query}'")
                        print(f"📝 English translation: '{english_query}'")
                        
                        # Check if translation seems incomplete
                        if len(english_query.split()) < 2:
                            print(f"⚠️ Translation seems incomplete, checking for common keywords...")
                            # Common Kannada health keywords
                            kannada_keywords = {
                                'jwara': 'fever',
                                'tala': 'head',
                                'novu': 'pain',
                                'kemmu': 'cough',
                                'ide': 'have'
                            }
                            # Replace Kannada words with English
                            for kannada, english in kannada_keywords.items():
                                if kannada in original_query.lower():
                                    english_query = english_query.replace(kannada, english)
                            print(f"✅ Enhanced translation: '{english_query}'")
                            
                except Exception as trans_error:
                    print(f"⚠️ ServVIA: Translation detection failed, using original: {trans_error}")
                    logger.warning(f"Translation error: {trans_error}")
                    english_query = original_query
                    detected_language = "en"
            
            # ============================================================
            # ✅ STEP 1.5: Check for greeting EARLY (before processing)
            # ============================================================
            greeting_keywords = [
                'hello', 'hi', 'hey', 'help', 'what can you', 'start', 'begin', 
                'greetings', 'good morning', 'good afternoon', 'good evening',
                'hola', 'bonjour', 'namaste', 'howdy', 'sup', 'yo'
            ]
            
            # Check if query is a greeting (case-insensitive)
            is_greeting = any(keyword in english_query.lower() for keyword in greeting_keywords)
            
            if is_greeting:
                print(f"✅ ServVIA: Detected greeting, returning welcome message")
                
                # ✅ FIXED: Use newlines (not HTML) - markdown will handle formatting
                welcome_message = """🏥 Hello! I'm ServVia.AI, your healthcare assistant. I can help you with:

Medical advice and information
Symptom checking
Home remedies
Medication guidance
Skin disease analysis (upload images)
Health tips based on your medical profile

How can I assist you today?"""
                
                # Translate if needed
                final_response = welcome_message
                
                if TRANSLATION_AVAILABLE and detected_language and detected_language.lower() != "en":
                    try:
                        print(f"🌐 ServVIA: Translating welcome to '{detected_language}'...")
                        final_response = asyncio.run(
                            translate_text_to_language(welcome_message, detected_language)
                        )
                        print(f"✅ ServVIA: Welcome message translated to {detected_language}")
                    except Exception as trans_error:
                        print(f"⚠️ Translation failed: {trans_error}")
                        final_response = welcome_message
                
                print(f"✅ ServVIA: Returning welcome message (greeting detected)")
                logger.info(f"✅ ServVIA: Welcome message sent to {user_email}")
                
                # Return immediately (skip all other processing)
                return JsonResponse({
                    "success": True,
                    "answer": final_response,
                    "message": final_response,
                    "response": final_response,
                    "source": "ServVia.AI",
                    "user": user_name,
                    "detected_language": detected_language,
                    "original_query": original_query,
                    "english_query": english_query,
                    "language_auto_detected": True,
                    "medical_profile_applied": False,  # No disclaimer on greeting
                    "content_filtered": False,
                    "ai_generated": False,
                    "is_greeting": True,
                    "status": "success"
                })
            
            # ============================================================
            # STEP 2: Get user's medical profile (for non-greetings)
            # ============================================================
            user_id = None
            medical_profile = None
            medical_disclaimer = ""
            
            if USER_MODEL_AVAILABLE and MEDICAL_FILTERING_AVAILABLE:
                try:
                    # ✅ FIXED: Get user ID from email
                    user = User.get(User.email == user_email)
                    user_id = str(user.id)
                    
                    # Get medical profile
                    medical_profile = get_medical_profile_by_user_id(user_id)
                    
                    if medical_profile:
                        print(f"✅ ServVIA: Medical profile found for {user_email}")
                        
                        # Generate medical disclaimer
                        conditions = []
                        if medical_profile.get('has_diabetes'):
                            conditions.append("diabetes")
                        if medical_profile.get('has_hypertension'):
                            conditions.append("high blood pressure")
                        if medical_profile.get('has_heart_disease'):
                            conditions.append("heart condition")
                        if medical_profile.get('has_kidney_disease'):
                            conditions.append("kidney disease")
                        if medical_profile.get('has_allergies') and medical_profile.get('allergies'):
                            allergies = ', '.join(medical_profile.get('allergies', []))
                            conditions.append(f"allergies to {allergies}")
                        if medical_profile.get('is_pregnant'):
                            conditions.append("pregnancy")
                        
                        if conditions:
                            medical_disclaimer = f"⚠️ Medical Note: Considering your {', '.join(conditions)}, I've personalized these recommendations for your safety. Always consult your healthcare provider before trying new remedies."
                    else:
                        print(f"ℹ️ ServVIA: No medical profile for {user_email}")
                        
                except Exception as profile_error:
                    print(f"⚠️ ServVIA: Could not retrieve medical profile: {profile_error}")
                    logger.warning(f"Medical profile error: {profile_error}")
            
            # ============================================================
            # STEP 3: Retrieve content from FarmStack API
            # ============================================================
            healthcare_response_english = ""
            content_source = None
            
            if FARMSTACK_AVAILABLE:
                try:
                    print("🏥 ServVIA: Querying FarmStack for healthcare content...")
                    
                    # ✅ Enhanced query for better results
                    search_query = english_query
                    
                    # Enhance common health queries
                    health_keywords = ['fever', 'headache', 'cough', 'cold', 'pain', 'stomach']
                    if any(keyword in english_query.lower() for keyword in health_keywords):
                        # Add "remedy" or "treatment" to get better results
                        if 'remedy' not in english_query.lower() and 'treatment' not in english_query.lower():
                            search_query = f"{english_query} remedy treatment"
                            print(f"🔍 Enhanced query for FarmStack: '{search_query}'")
                    
                    # Query FarmStack API
                    retrieved_content = retrieve_content_from_api(
                        query=search_query,
                        user_email=user_email,
                        apply_medical_filter=True
                    )
                    
                    if retrieved_content and len(retrieved_content) > 0:
                        print(f"✅ ServVIA: Retrieved {len(retrieved_content)} content chunks from FarmStack")
                        content_source = "FarmStack Knowledge Base"
                        
                        # ============================================================
                        # STEP 4: Additional medical filtering
                        # ============================================================
                        if MEDICAL_FILTERING_AVAILABLE and medical_profile and user_id:
                            print("🔍 ServVIA: Applying medical profile filter...")
                            
                            safe_content, warnings, filter_disclaimer = filter_remedies_by_medical_profile(
                                content=retrieved_content,
                                user_id=user_id
                            )
                            
                            if safe_content and len(safe_content) > 0:
                                print(f"✅ ServVIA: {len(safe_content)}/{len(retrieved_content)} chunks passed medical filter")
                                retrieved_content = safe_content
                                
                                if filter_disclaimer:
                                    medical_disclaimer = filter_disclaimer
                            else:
                                print("⚠️ ServVIA: All content filtered out by medical profile")
                                healthcare_response_english = f"Hello {user_name}! Based on your medical profile, I couldn't find remedies that are safe for your specific conditions regarding '{original_query}'. Please consult your healthcare provider for personalized advice. 🏥"
                                retrieved_content = []
                        
                        # ============================================================
                        # STEP 5: Generate response with OpenAI
                        # ============================================================
                        if retrieved_content and GENERATION_AVAILABLE:
                            try:
                                print("🤖 ServVIA: Generating response with OpenAI...")
                                
                                context_chunks = "\n\n".join(retrieved_content[:5])
                                
                                response_map = asyncio.run(
                                    generate_query_response(
                                        original_query=original_query,
                                        user_name=user_name,
                                        context_chunks=context_chunks,
                                        rephrased_query=english_query
                                    )
                                )
                                
                                healthcare_response_english = response_map.get('response')
                                
                                # ✅ CRITICAL: Clean bullets/numbers from AI response
                                healthcare_response_english = clean_ai_response_formatting(healthcare_response_english)
                                
                                if healthcare_response_english:
                                    print(f"✅ ServVIA: Healthcare response generated with OpenAI (formatted)")
                                else:
                                    print(f"⚠️ ServVIA: OpenAI returned empty response, using fallback")
                                    healthcare_response_english = f"Hello {user_name}! Based on available information:\n\n{retrieved_content[0][:500]}..."
                                    
                            except Exception as gen_error:
                                print(f"❌ Generation error: {gen_error}")
                                logger.error(f"OpenAI generation error: {gen_error}", exc_info=True)
                                healthcare_response_english = f"Hello {user_name}! Based on available information:\n\n{retrieved_content[0][:500]}..."
                                
                        elif retrieved_content and not GENERATION_AVAILABLE:
                            print("ℹ️ ServVIA: Using content directly (no AI generation)")
                            healthcare_response_english = f"Hello {user_name}! Based on available information:\n\n{retrieved_content[0][:500]}..."
                            
                    else:
                        print("⚠️ ServVIA: No content retrieved from FarmStack")
                        healthcare_response_english = f"Hello {user_name}! I couldn't find specific information about '{original_query}' in my healthcare knowledge base. For your health and safety, please consult a healthcare professional. 🏥"
                    
                except Exception as farmstack_error:
                    print(f"❌ ServVIA FarmStack Error: {farmstack_error}")
                    logger.error(f"FarmStack API Error: {farmstack_error}", exc_info=True)
                    healthcare_response_english = f"Hello {user_name}! I'm experiencing technical difficulties accessing the healthcare database. Please consult a healthcare professional for medical advice. 🏥"
            else:
                # FarmStack not available
                healthcare_response_english = f"Hello {user_name}! I understand you're asking about '{original_query}'. For your health and safety, please consult a healthcare professional for specific medical advice. 🏥"
            
            # ============================================================
            # STEP 6: Add medical disclaimer to response
            # ============================================================
            if medical_disclaimer and healthcare_response_english:
                healthcare_response_english = f"{medical_disclaimer}\n\n{healthcare_response_english}"
            
            # ============================================================
            # STEP 7: Translate response back to user's detected language
            # ============================================================
            final_response = healthcare_response_english
            
            if TRANSLATION_AVAILABLE and detected_language and detected_language.lower() != "en":
                try:
                    print(f"🌐 ServVIA: Translating response to '{detected_language}'...")
                    final_response = asyncio.run(
                        translate_text_to_language(healthcare_response_english, detected_language)
                    )
                    print(f"✅ ServVIA: Response translated successfully to {detected_language}")
                except Exception as trans_error:
                    print(f"⚠️ ServVIA: Response translation failed: {trans_error}")
                    logger.warning(f"Translation error: {trans_error}")
                    final_response = healthcare_response_english
            else:
                print(f"ℹ️ ServVIA: Keeping response in English (detected: {detected_language})")
            
            # ============================================================
            # STEP 8: Build response data
            # ============================================================
            response_data = {
                "success": True,
                "answer": final_response,
                "message": final_response,
                "response": final_response,
                "source": content_source or "FarmStack",
                "user": user_name,
                "detected_language": detected_language,
                "original_query": original_query,
                "english_query": english_query,
                "language_auto_detected": True,
                "medical_profile_applied": medical_profile is not None,
                "content_filtered": MEDICAL_FILTERING_AVAILABLE and medical_profile is not None,
                "ai_generated": GENERATION_AVAILABLE,
                "status": "success"
            }
            
            print(f"✅ ServVIA: Complete response generated for {user_email}")
            logger.info(f"✅ ServVIA: Request completed successfully for {user_email}")
            
            return JsonResponse(response_data)
                
        except Exception as e:
            print(f"❌ ServVIA Endpoint Error: {e}")
            logger.error(f"ServVIA Endpoint Error: {e}", exc_info=True)
            return JsonResponse({
                "success": False,
                "answer": "I'm experiencing technical difficulties. Please consult a healthcare professional for medical advice.",
                "message": "I'm experiencing technical difficulties. Please consult a healthcare professional for medical advice.",
                "error": str(e),
                "status": "error"
            }, status=500)
    
    # Handle other methods
    return JsonResponse({
        "error": "Method not allowed",
        "allowed_methods": ["GET", "POST", "OPTIONS"]
    }, status=405)