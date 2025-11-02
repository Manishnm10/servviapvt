import asyncio, aiohttp, logging, uuid
from google.cloud import texttospeech
from google.oauth2 import service_account

from common.constants import Constants
from common.utils import clean_text
from language_service.utils import get_language_by_code
from django_core.config import Config

logger = logging.getLogger(__name__)


credentials = service_account.Credentials.from_service_account_file(Config.GOOGLE_APPLICATION_CREDENTIALS)


async def synthesize_speech_azure(text_to_synthesize, language_code, aiohttp_session):
    """
    Synthesise speech using Azure TTS model.
    `Azure TTS Docs <https://learn.microsoft.com/en-us/azure/ai-services/speech-service/>`_
    """
    audio_content = None

    # use Azure for Speech synthesis
    url = f"https://{Config.AZURE_SERVICE_REGION}.tts.speech.microsoft.com/cognitiveservices/v1"
    headers = {
        "Ocp-Apim-Subscription-Key": Config.AZURE_SUBSCRIPTION_KEY,
        "Content-Type": "application/ssml+xml",
        "X-Microsoft-OutputFormat": "ogg-48khz-16bit-mono-opus",
    }

    AZURE_VOICE = "en-GB-SoniaNeural"
    if language_code == "en-KE":
        AZURE_VOICE = "en-KE-AsiliaNeural"

    elif language_code == "sw-KE":
        AZURE_VOICE = "sw-KE-ZuriNeural"

    elif language_code == "en-NG":
        AZURE_VOICE = "en-NG-EzinneNeural"

    # The body of the request. Replace the text you want to synthesize
    body = f"""
    <speak version='1.0' xml:lang='{language_code}'>
        <voice xml:lang='{language_code}' xml:gender='Female' name='{AZURE_VOICE}'>
            {text_to_synthesize}
        </voice>
    </speak>
    """
    # Making the POST request to the Azure service
    # response = requests.post(url, headers=headers, data=body)

    async with aiohttp_session.post(url, data=body, headers=headers) as response:
        audio_content = await response.read() if response.status == 200 else None

    return audio_content


async def synthesize_speech(
    input_text: str,
    input_language: str,
    id_string: str = None,
    aiohttp_session=None,
    audio_encoding_format=texttospeech.AudioEncoding.OGG_OPUS,
    sample_rate_hertz=48000,
) -> str:
    """
    Synthesise speech using Google TTS. Please refer the below docs.
    `Google TTS Docs <https://cloud.google.com/text-to-speech/docs/>`_
    """
    id_string = uuid.uuid4() if not id_string else id_string
    file_name = f"response_{id_string}.{Constants.OGG}"
    input_text = clean_text(input_text)
    
    # 🔧 FIX: Validate input text
    if not input_text or input_text.strip() == "":
        logger.error("❌ Empty text provided for speech synthesis")
        return None
    
    synthesis_input = texttospeech.SynthesisInput(text=input_text)
    language_code = "en-US"  # 🔧 FIX: Default to en-US instead of en-IN
    input_language = input_language.split("-")[0] if "-" in input_language else input_language

    if audio_encoding_format and str(audio_encoding_format).lower() == Constants.MP3:
        audio_encoding_format = texttospeech.AudioEncoding.MP3
        file_name = f"response_{id_string}.{Constants.MP3}"
    else:
        audio_encoding_format = texttospeech.AudioEncoding.OGG_OPUS

    sample_rate_hertz = sample_rate_hertz if sample_rate_hertz else 48000

    try:
        language = get_language_by_code(input_language)
        if language:
            language_code = language.get("bcp_code")
            logger.info(f"🌐 Using BCP code: {language_code} for language: {input_language}")
        else:
            # 🔧 FIX: Map common language codes
            language_map = {
                "en": "en-US",
                "hi": "hi-IN",
                "kn": "kn-IN",
                "ta": "ta-IN",
                "te": "te-IN",
                "es": "es-ES",
                "fr": "fr-FR",
                "de": "de-DE"
            }
            language_code = language_map.get(input_language, "en-US")
            logger.warning(f"⚠️ Language {input_language} not in database, using: {language_code}")

        # Use Google TTS for speech synthesis
        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code,
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=audio_encoding_format, sample_rate_hertz=sample_rate_hertz
        )
        text_to_speech_client = texttospeech.TextToSpeechClient(credentials=credentials)

        try:
            response = await asyncio.to_thread(
                text_to_speech_client.synthesize_speech,
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config,
            )
            audio_content = response.audio_content

        except Exception as e:
            logger.error(f"❌ Error while synthesizing speech: {str(e)}", exc_info=True)
            return None

        with open(file_name, "wb") as out:
            out.write(audio_content)
            logger.info(f"✅ Successfully wrote voice response to file: {file_name}")

    except Exception as e:
        logger.error(f"❌ TTS Error: {e}", exc_info=True)
        return None

    return file_name