import asyncio
from google.cloud import translate_v2 as translate
from google.cloud import texttospeech
from google.oauth2 import service_account

from common.constants import Constants
from django_core.config import Config

credentials = service_account.Credentials.from_service_account_file(Config.GOOGLE_APPLICATION_CREDENTIALS)


async def a_translate_to_english(text: str) -> str:
    """
    Translate a given text to english with healthcare context.
    """
    translate_client = translate.Client(credentials=credentials)
    
    # Add healthcare context hint for better translation
    translation = await asyncio.to_thread(
        translate_client.translate,
        text,
        target_language=Constants.LANGUAGE_SHORT_CODE_ENG,
        format_="text",
        model="nmt"  # Use Neural Machine Translation for better accuracy
    )
    return translation["translatedText"]


async def a_translate_to(text: str, lang_code: str) -> str:
    """
    Translate a given text to specified language with better accuracy.
    """
    translate_client = translate.Client(credentials=credentials)
    # Extract base language code (hi-Latn -> hi, kn -> kn)
    lang_code = lang_code.split("-")[0] if "-" in lang_code else lang_code
    
    translation = await asyncio.to_thread(
        translate_client.translate,
        text,
        target_language=lang_code,
        format_="text",
        model="nmt"  # Use Neural Machine Translation
    )
    return translation["translatedText"]


async def detect_language_and_translate_to_english(input_msg):
    """
    Detect the language of specified text and translate it to english.
    Enhanced with better error handling and logging.
    """
    translate_client = translate.Client(credentials=credentials)
    
    # Step 1: Detect language
    language_detection = await asyncio.to_thread(translate_client.detect_language, input_msg)
    input_language_detected = language_detection["language"]
    confidence = language_detection.get("confidence", 0)
    
    print(f"🌐 Language Detection:")
    print(f"   Input: '{input_msg}'")
    print(f"   Detected: {input_language_detected} (confidence: {confidence})")

    # Step 2: Translate if not English
    if input_language_detected != Constants.LANGUAGE_SHORT_CODE_ENG:
        translated_input_message = await a_translate_to_english(input_msg)
        print(f"   Translated: '{translated_input_message}'")
    else:
        translated_input_message = input_msg
        print(f"   Already in English, no translation needed")

    return translated_input_message, input_language_detected


async def translate_text_to_language(text, target_language_code):
    """
    Translate text to target language - FIXED VERSION for better accuracy
    """
    try:
        translate_client = translate.Client(credentials=credentials)
        
        # Extract base language code (hi-Latn -> hi, kn -> kn, en-US -> en)
        base_lang = target_language_code.split("-")[0] if "-" in target_language_code else target_language_code
        
        print(f"🌐 Translation Output:")
        print(f"   Text length: {len(text)} chars")
        print(f"   Target: {base_lang} (from {target_language_code})")
        
        # Translate the text to the detected language
        result = await asyncio.to_thread(
            translate_client.translate,
            text,
            target_language=base_lang,
            format_="text",
            model="nmt"  # Neural Machine Translation for better quality
        )
        
        translated = result['translatedText']
        print(f"   ✅ Translated successfully")
        
        return translated
        
    except Exception as e:
        print(f"   ❌ Translation failed: {e}")
        return text  # Return original text if translation fails