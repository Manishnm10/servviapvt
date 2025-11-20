import asyncio
import datetime
import json
import logging
import os
import uuid

# Priority 1: Try local content retrieval for RAG
try:
    from healthcare.local_content_retriever import retrieve_from_local_content, is_initialized
    LOCAL_CONTENT_AVAILABLE = is_initialized()
    
    logger_temp = logging.getLogger(__name__)
    if LOCAL_CONTENT_AVAILABLE:
        logger_temp.info("✅ ServVIA: RAG with local content available")
    else:
        logger_temp.warning("⚠️ ServVIA: RAG collection is empty, run: python healthcare/ingest_content.py")
        
except ImportError as e:
    LOCAL_CONTENT_AVAILABLE = False
    logger_temp = logging.getLogger(__name__)
    logger_temp.warning(f"⚠️ ServVIA: Local content not available: {e}")

# Priority 2: Fallback to simple PDF handler
try:
    from healthcare.pdf_content_handler import get_healthcare_response_from_pdf
    HEALTHCARE_PDF_AVAILABLE = True
except ImportError:
    HEALTHCARE_PDF_AVAILABLE = False

from common.constants import Constants
from common.utils import (
    create_or_update_user_by_email,
    decode_base64_to_binary,
    encode_binary_to_base64,
    fetch_corresponding_multilingual_text,
    fetch_multilingual_texts_for_static_text_messages,
    get_message_object_by_id,
    get_or_create_latest_conversation,
    get_or_create_user_by_email,
    get_user_by_email,
    get_user_chat_history,
    insert_message_record,
    postprocess_and_translate_query_response,
    save_message_obj,
    send_request,
)
from database.database_config import db_conn
from database.db_operations import update_record, get_record_by_field
from database.models import User
from django_core.config import Config
from intent_classification.intent import process_user_intent
from language_service.asr import transcribe_and_translate
from language_service.translation import (
    a_translate_to,
    detect_language_and_translate_to_english,
)
from language_service.tts import synthesize_speech
from language_service.utils import get_language_by_id
from rag_service.execute_rag import execute_rag_pipeline

logger = logging.getLogger(__name__)


def authenticate_user_based_on_email(email_id):
    """
    Authenticate the user via external API, database, or auto-authentication
    Priority: External API > Database > Auto-create
    """
    authenticated_user = None
    
    try:
        # Priority 1: Try external API if configured
        if Config.CONTENT_DOMAIN_URL and Config.CONTENT_AUTHENTICATE_ENDPOINT:
            try:
                authentication_url = (
                    f"{Config.CONTENT_DOMAIN_URL}{Config.CONTENT_AUTHENTICATE_ENDPOINT}"
                )
                response = send_request(
                    authentication_url,
                    data={"email": email_id},
                    content_type="JSON",
                    request_type="POST",
                    total_retry=3,
                )
                authenticated_user = (
                    json.loads(response.text)
                    if response and response.status_code == 200
                    else None
                )
                
                if authenticated_user:
                    logger.info(f"✅ External API authentication successful: {email_id}")
                    return authenticated_user
            except Exception as api_error:
                logger.warning(f"⚠️ External API failed: {api_error}, trying database auth")
        
        # Priority 2: Try database authentication
        if Config.WITH_DB_CONFIG:
            try:
                user = get_record_by_field(User, "email", email_id)
                
                if user:
                    authenticated_user = {
                        'email': user.email,
                        'first_name': user.first_name or email_id.split('@')[0],
                        'last_name': user.last_name or '',
                        'phone_number': user.phone if hasattr(user, 'phone') else None
                    }
                    logger.info(f"✅ Database authentication successful: {email_id}")
                    return authenticated_user
            except Exception as db_error:
                logger.warning(f"⚠️ Database authentication failed: {db_error}, using auto-auth")
        
        # Priority 3: Auto-authenticate for development
        if not authenticated_user:
            email_name = email_id.split('@')[0] if '@' in email_id else 'User'
            authenticated_user = {
                'email': email_id,
                'first_name': email_name.capitalize(),
                'last_name': '',
                'phone_number': None
            }
            logger.info(f"✅ Auto-authentication for development: {email_id}")

    except Exception as error:
        logger.error(f"❌ Authentication error: {error}", exc_info=True)
        
        # Last resort: create basic auth object
        email_name = email_id.split('@')[0] if '@' in email_id else 'User'
        authenticated_user = {
            'email': email_id,
            'first_name': email_name.capitalize(),
            'last_name': '',
            'phone_number': None
        }
        logger.info(f"✅ Fallback authentication: {email_id}")

    return authenticated_user


def preprocess_user_data(
    original_query,
    email_id,
    authenticated_user={},
    with_db_config=Config.WITH_DB_CONFIG,
    message_input_type=Constants.MESSAGE_INPUT_TYPE_TEXT,
):
    """
    Process user profile fetched from content authenticate site by saving or updating.
    """
    user_name, message_id, message_obj, user_id = None, None, None, None
    user_data, message_data_to_insert_or_update = {}, {}

    try:
        if len(authenticated_user) >= 1:
            user_data.update({"user_name": authenticated_user.get("first_name")})

        if with_db_config and len(authenticated_user) >= 1:
            user_obj = create_or_update_user_by_email(
                {
                    "email": email_id,
                    "phone": authenticated_user.get("phone_number", None),
                    "first_name": authenticated_user.get("first_name", None),
                    "last_name": authenticated_user.get("last_name", None),
                }
            )
            user_id = user_obj.id
            user_name = user_obj.first_name

            conversation_obj = get_or_create_latest_conversation(
                {"user_id": user_id, "title": original_query}
            )
            message_obj = insert_message_record(
                {
                    "original_message": original_query,
                    "conversation_id": conversation_obj,
                }
            )
            message_id = message_obj.id
            message_data_to_insert_or_update["input_type"] = message_input_type
            message_data_to_insert_or_update["message_input_time"] = (
                datetime.datetime.now()
            )

            user_data.update(
                {"user_id": user_id, "user_name": user_name, "message_id": message_id}
            )

    except Exception as error:
        logger.error(error, exc_info=True)

    finally:
        if message_obj and message_id:
            save_message_obj(message_id, message_data_to_insert_or_update)

    return user_data, message_obj


def process_query(original_query, email_id, authenticated_user={}):
    """
    Pre-process user profile and user query, execute RAG pipeline with local content
    or fallback to PDF handler, and return the generated response.
    """
    message_obj, chat_history = None, None
    (
        response_map,
        message_data_to_insert_or_update,
        message_data_update_post_rag_pipeline,
    ) = ({}, {}, {})

    try:
        user_data, message_obj = preprocess_user_data(
            original_query, email_id, authenticated_user
        )
        # fetch user chat history
        user_id = user_data.get("user_id", None)
        user_name = user_data.get("user_name", None)
        message_id = user_data.get("message_id", None)
        chat_history = get_user_chat_history(user_id) if user_id else None

        # Get user name for healthcare responses
        if not user_name:
            user_name = authenticated_user.get("first_name", "there")
            if not user_name or user_name.strip() == '':
                user_name = email_id.split('@')[0] if '@' in email_id else 'there'

        # begin translating original query to english
        message_data_to_insert_or_update["input_translation_start_time"] = (
            datetime.datetime.now()
        )
        query_in_english, input_language_detected = asyncio.run(
            detect_language_and_translate_to_english(original_query)
        )
        message_data_to_insert_or_update["translated_message"] = query_in_english
        message_data_to_insert_or_update["input_translation_end_time"] = (
            datetime.datetime.now()
        )
        message_data_to_insert_or_update["input_language_detected"] = (
            input_language_detected
        )
        # end of translating original query to english

        # Priority 1: Use full RAG pipeline if local content is available
        if LOCAL_CONTENT_AVAILABLE:
            logger.info("🧠 ServVIA: Using full RAG pipeline with local healthcare content")
            
            # Execute full RAG pipeline (will use local content in retrieval step)
            response_map, message_data_update_post_rag_pipeline = execute_rag_pipeline(
                query_in_english,
                input_language_detected,
                email_id,
                user_name=user_name,
                message_id=message_id,
                chat_history=chat_history,
            )
            
        # Priority 2: Use simple PDF handler as fallback
        elif HEALTHCARE_PDF_AVAILABLE:
            logger.info("📄 ServVIA: Using simple PDF handler (fallback)")
            
            # Generate healthcare response from PDF
            healthcare_response = get_healthcare_response_from_pdf(original_query, user_name)
            
            # Create response map
            response_map.update({
                "generated_final_response": healthcare_response,
                "source": "Home_Remedies_Guide.pdf",
                "message_id": message_id
            })
            
        # Priority 3: Use original intent processing and RAG pipeline
        else:
            logger.info("🔄 ServVIA: Using original RAG pipeline (no local content)")
            
            intent_response, user_intent, proceed_to_rag = asyncio.run(
                process_user_intent(original_query, user_name)
            )

            if not proceed_to_rag:
                # do not execute rag pipeline
                response_map.update({"generated_final_response": intent_response})
            else:
                # execute rag pipeline further
                response_map, message_data_update_post_rag_pipeline = execute_rag_pipeline(
                    query_in_english,
                    input_language_detected,
                    email_id,
                    user_name=user_name,
                    message_id=message_id,
                    chat_history=chat_history,
                )

        # translate back to the detected input language of the original query
        # begin translating original response to input_language_detected
        (
            translated_response,
            final_response,
            follow_up_question_options,
            follow_up_question_data_to_insert,
        ) = asyncio.run(
            postprocess_and_translate_query_response(
                response_map.get("generated_final_response"),
                input_language_detected,
                str(message_id),
            )
        )
        # end translating original response to input_language_detected

        # Add healthcare-specific follow-up questions
        if LOCAL_CONTENT_AVAILABLE or HEALTHCARE_PDF_AVAILABLE:
            healthcare_followups = [
                "What are the warning signs I should watch for?",
                "How can I prevent this condition in the future?", 
                "Are there any foods or activities I should avoid?",
                "When should I see a doctor for this condition?"
            ]
            follow_up_question_options = healthcare_followups

        response_map.update(
            {
                "translated_response": translated_response,
                "final_response": final_response,
                "source": response_map.get("source", "Healthcare Content" if LOCAL_CONTENT_AVAILABLE else None),
                "follow_up_questions": follow_up_question_options,
            }
        )

        message_data_to_insert_or_update["message_response"] = final_response
        message_data_to_insert_or_update["message_translated_response"] = (
            translated_response
        )
        message_data_to_insert_or_update.update(message_data_update_post_rag_pipeline)

        # Log ServVIA healthcare activity
        if LOCAL_CONTENT_AVAILABLE:
            logger.info(f"🧠 ServVIA RAG response generated for user: {user_name}, query: {original_query}")
        elif HEALTHCARE_PDF_AVAILABLE:
            logger.info(f"📄 ServVIA PDF response generated for user: {user_name}, query: {original_query}")

    except Exception as error:
        logger.error(f"❌ ServVIA Error in process_query: {error}", exc_info=True)
        
        # Fallback healthcare response in case of error
        user_name = user_name if 'user_name' in locals() and user_name else "there"
        fallback_response = f"Hello {user_name}! 👋 I'm experiencing some technical difficulties with my healthcare system right now. For your safety, please consult a healthcare professional for medical advice. 🏥"
        
        response_map.update({
            "translated_response": fallback_response,
            "final_response": fallback_response,
            "source": None,
            "follow_up_questions": [
                "Contact your healthcare provider", 
                "Visit urgent care if symptoms persist", 
                "Call emergency services if severe"
            ]
        })

    finally:
        if message_obj and message_id:
            save_message_obj(message_id, message_data_to_insert_or_update)

    return response_map


def process_input_audio_to_base64(
    original_text,
    message_id=None,
    language_code=Constants.LANGUAGE_SHORT_CODE_NATIVE,
    with_db_config=Config.WITH_DB_CONFIG,
):
    """
    Synthesise input text or user query to audio in specified language, and encode to base64 string.
    """
    input_audio, input_audio_file = None, None

    try:
        translated_text = asyncio.run(a_translate_to(original_text, language_code))
        input_audio_file = asyncio.run(
            synthesize_speech(str(translated_text), language_code, message_id)
        )
        input_audio = encode_binary_to_base64(input_audio_file)

    except Exception as error:
        logger.error(error, exc_info=True)

    finally:
        if input_audio_file and os.path.exists(input_audio_file):
            try:
                os.remove(input_audio_file)
            except Exception as e:
                logger.warning(f"⚠️ Could not delete temp file: {e}")

    return input_audio


def process_output_audio(
    original_text, message_id=None, with_db_config=Config.WITH_DB_CONFIG
):
    """
    Synthesise output text or generated response to audio in detected language, and encode to base64 string.
    """
    response_audio, response_audio_file, message_obj = None, None, None
    message_data_to_insert_or_update = {}
    input_language_detected = "en"

    try:
        if with_db_config and message_id:
            message_obj = get_message_object_by_id(message_id)
            input_language_detected = message_obj.input_language_detected or "en"
        else:
            try:
                query_in_english, input_language_detected = asyncio.run(
                    detect_language_and_translate_to_english(original_text)
                )
                logger.info(f"🌐 Detected language for TTS: {input_language_detected}")
            except Exception as lang_error:
                logger.warning(f"⚠️ Language detection failed: {lang_error}, using English")
                input_language_detected = "en"

        message_data_to_insert_or_update["response_text_to_speech_start_time"] = (
            datetime.datetime.now()
        )
        
        logger.info(f"🔊 Synthesizing speech for text: '{original_text[:50]}...' in language: {input_language_detected}")
        
        response_audio_file = asyncio.run(
            synthesize_speech(str(original_text), input_language_detected, message_id)
        )
        
        message_data_to_insert_or_update["response_text_to_speech_end_time"] = (
            datetime.datetime.now()
        )

        if response_audio_file and os.path.exists(response_audio_file):
            response_audio = encode_binary_to_base64(response_audio_file)
            logger.info(f"✅ Audio synthesis successful, file size: {os.path.getsize(response_audio_file)} bytes")
        else:
            logger.error(f"❌ Audio file not created: {response_audio_file}")
            response_audio = None

    except Exception as error:
        logger.error(f"❌ process_output_audio error: {error}", exc_info=True)

    finally:
        if message_obj and message_id:
            save_message_obj(message_id, message_data_to_insert_or_update)

        if response_audio_file and os.path.exists(response_audio_file):
            try:
                os.remove(response_audio_file)
            except Exception as e:
                logger.warning(f"⚠️ Could not delete temp file: {e}")

    return response_audio


def handle_input_query(input_query):
    """
    Return a binary file by decoding input query (as base64 string).
    """
    file_name, input_query_file = None, None

    input_query_file = decode_base64_to_binary(input_query)

    if input_query_file:
        file_name = f"{uuid.uuid4()}_audio_input.{Constants.MP3}"
        with open(file_name, "wb") as output_file_buffer:
            output_file_buffer.write(input_query_file)

    return file_name


def process_transcriptions(
    voice_file,
    email_id,
    authenticated_user={},
    language_code=Constants.LANGUAGE_SHORT_CODE_NATIVE,
    language_bcp_code=Constants.LANGUAGE_BCP_CODE_NATIVE,
    message_input_type=Constants.MESSAGE_INPUT_TYPE_VOICE,
    with_db_config=Config.WITH_DB_CONFIG,
):
    """
    Process generation of transcriptions (text) for a given audio or voice file
    in a specified language if any or in user preferred language.
    """
    message_id, message_obj = None, None
    response_map, message_data_to_insert_or_update, language_dict = {}, {}, {}

    try:
        if with_db_config:
            user = get_user_by_email(email_id)
            user_id = user.get("user_id")
            language_dict = get_language_by_id(user.get("preferred_language_id"))
            language_code = language_dict.get("code", language_code)

        text_codes_list_with_multilingual_texts = (
            fetch_multilingual_texts_for_static_text_messages(
                [Constants.COULD_NOT_UNDERSTAND_MESSAGE], language_code
            )
        )
        could_not_understand_message = fetch_corresponding_multilingual_text(
            Constants.COULD_NOT_UNDERSTAND_MESSAGE,
            text_codes_list_with_multilingual_texts,
        )

        message_data_to_insert_or_update["message_input_time"] = datetime.datetime.now()
        message_data_to_insert_or_update["input_speech_to_text_start_time"] = (
            datetime.datetime.now()
        )
        transcriptions, detected_language, confidence_score = asyncio.run(
            transcribe_and_translate(voice_file, language_bcp_code)
        )

        message_data_to_insert_or_update["input_speech_to_text_end_time"] = (
            datetime.datetime.now()
        )
        response_map["confidence_score"] = confidence_score
        response_map["transcriptions"] = transcriptions

        if confidence_score < Constants.ASR_DEFAULT_CONFIDENCE_SCORE:
            message_data_to_insert_or_update["message_response"] = (
                could_not_understand_message
            )
            message_data_to_insert_or_update["message_translated_response"] = (
                could_not_understand_message
            )
            message_data_to_insert_or_update["message_response_time"] = (
                datetime.datetime.now()
            )
            message_data_to_insert_or_update["input_type"] = message_input_type
            response_map["transcriptions"] = could_not_understand_message

        user_data, message_obj = preprocess_user_data(
            transcriptions, email_id, authenticated_user
        )
        message_id = user_data.get("message_id", None)
        response_map["message_id"] = message_id

    except Exception as error:
        logger.error(error, exc_info=True)

    finally:
        if message_obj and message_id:
            save_message_obj(message_id, message_data_to_insert_or_update)

        if voice_file and os.path.exists(voice_file):
            try:
                os.remove(voice_file)
            except Exception as e:
                logger.warning(f"⚠️ Could not delete temp file: {e}")

    return response_map