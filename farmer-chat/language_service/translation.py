import asyncio
from google.cloud import translate_v2 as translate
from google.cloud import texttospeech
from google.oauth2 import service_account

from common.constants import Constants
from django_core.config import Config

credentials = service_account.Credentials.from_service_account_file(Config.GOOGLE_APPLICATION_CREDENTIALS)


# ========================================
# KANNADA MEDICAL DICTIONARY
# ========================================
KANNADA_MEDICAL_PHRASES = {
    # Fever related
    "nanige jwara ide": "I have fever",
    "ನನಗೆ ಜ್ವರ ಇದೆ": "I have fever",
    "jwara": "fever",
    "ಜ್ವರ": "fever",
    "jwara bantide": "I got fever",
    "jwara ide": "there is fever",
    
    # Headache related
    "nanige thalenovu ide": "I have headache",
    "ನನಗೆ ತಲೆನೋವು ಇದೆ": "I have headache",
    "thalenovu": "headache",
    "ತಲೆನೋವು": "headache",
    "thale novu": "headache",
    "tale novu": "head pain",
    
    # Cough related
    "nanige kemmu ide": "I have cough",
    "ನನಗೆ ಕೆಮ್ಮು ಇದೆ": "I have cough",
    "kemmu": "cough",
    "ಕೆಮ್ಮು": "cough",
    "kemmu barthide": "I am coughing",
    
    # Cold related
    "nanige sali ide": "I have cold",
    "ನನಗೆ ಶೀತ ಇದೆ": "I have cold",
    "sali": "cold",
    "sardi": "cold",
    "sardi ide": "have cold",
    
    # Stomach pain
    "nanige hotte novu ide": "I have stomach pain",
    "ನನಗೆ ಹೊಟ್ಟೆ ನೋವು ಇದೆ": "I have stomach ache",
    "hotte novu": "stomach pain",
    "ಹೊಟ್ಟೆ ನೋವು": "stomach ache",
    
    # Body pain
    "nanige shareera novu ide": "I have body pain",
    "ನನಗೆ ಶರೀರ ನೋವು ಇದೆ": "I have body ache",
    "shareera novu": "body pain",
    "ಶರೀರ ನೋವು": "body pain",
    
    # Weakness
    "nanige kamjori ide": "I feel weak",
    "kamjori": "weakness",
    
    # Vomiting
    "nanige hanti barthide": "I am vomiting",
    "hanti": "vomiting",
    
    # Diarrhea
    "nanige jolluhagu ide": "I have diarrhea",
    "jolluhagu": "loose motion",
}


def check_kannada_medical(text):
    """
    Check if text matches Kannada medical dictionary
    Returns translated text or None
    """
    if not text:
        return None
    
    text_lower = text.lower().strip()
    
    # Check for exact match (case-insensitive)
    if text_lower in KANNADA_MEDICAL_PHRASES:
        return KANNADA_MEDICAL_PHRASES[text_lower]
    
    # Check original text (for Kannada script)
    if text.strip() in KANNADA_MEDICAL_PHRASES:
        return KANNADA_MEDICAL_PHRASES[text.strip()]
    
    return None


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
    Enhanced with Kannada medical dictionary for better accuracy.
    """
    # Step 0: Check Kannada medical dictionary first
    dict_translation = check_kannada_medical(input_msg)
    
    if dict_translation:
        print(f"🏥 Medical Dictionary Match:")
        print(f"   Input: '{input_msg}'")
        print(f"   Translation: '{dict_translation}'")
        print(f"   Source: Kannada Medical Dictionary")
        return dict_translation, "kn"
    
    # Step 1: Detect language with Google
    translate_client = translate.Client(credentials=credentials)
    
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