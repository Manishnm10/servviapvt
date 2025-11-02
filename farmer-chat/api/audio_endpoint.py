from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import logging
import tempfile
import os
import base64
import io

logger = logging.getLogger(__name__)

# Try to import speech recognition
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
    print("✅ Speech Recognition available")
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    print("❌ Speech Recognition not available - install with: pip install SpeechRecognition")

# Try to import pydub for audio conversion
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
    print("✅ Pydub available for audio conversion")
except ImportError:
    PYDUB_AVAILABLE = False
    print("❌ Pydub not available - install with: pip install pydub")

# Try to import Google Cloud Speech (if available)
try:
    from google.cloud import speech
    GOOGLE_SPEECH_AVAILABLE = True
    print("✅ Google Cloud Speech available")
except ImportError:
    GOOGLE_SPEECH_AVAILABLE = False
    print("❌ Google Cloud Speech not available")

@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def transcribe_audio(request):
    """
    Transcribe audio to text for ServVIA
    """
    
    if request.method == "OPTIONS":
        response = JsonResponse({})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type"
        return response
    
    temp_input_path = None
    temp_wav_path = None
    
    try:
        print("🎤 ServVIA: Audio transcription request received")
        
        # Parse request data
        if request.content_type == 'application/json':
            data = json.loads(request.body) if request.body else {}
        else:
            data = dict(request.POST)
        
        # Get audio data from request
        audio_base64 = data.get('query', '')
        email_id = data.get('email_id', 'user@servvia.com')
        language_code = data.get('query_language_bcp_code', 'en-US')
        
        # Handle list values
        if isinstance(audio_base64, list):
            audio_base64 = audio_base64[0] if audio_base64 else ''
        if isinstance(email_id, list):
            email_id = email_id[0] if email_id else 'user@servvia.com'
        if isinstance(language_code, list):
            language_code = language_code[0] if language_code else 'en-US'
        
        if not audio_base64:
            print("❌ No audio data found in request")
            return JsonResponse({
                "success": False,
                "error": "No audio data provided",
                "heard_input_query": "",
                "confidence_score": 0,
                "message": "Please speak into the microphone and try again."
            }, status=400)
        
        print(f"🎤 Processing audio data (length: {len(audio_base64)} chars)")
        
        # Decode base64 audio
        try:
            # Remove data URL prefix if present
            if ',' in audio_base64[:100]:
                audio_base64 = audio_base64.split(',', 1)[1]
            
            audio_data = base64.b64decode(audio_base64)
            print(f"✅ Decoded audio data: {len(audio_data)} bytes")
        except Exception as decode_error:
            print(f"❌ Failed to decode base64 audio: {decode_error}")
            return JsonResponse({
                "success": False,
                "error": "Invalid audio data format",
                "heard_input_query": "",
                "confidence_score": 0,
                "message": "Audio encoding error. Please try again."
            }, status=400)
        
        # Save original audio to temporary file
        try:
            with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as temp_audio:
                temp_audio.write(audio_data)
                temp_input_path = temp_audio.name
                print(f"✅ Saved audio to temp file: {temp_input_path}")
        except Exception as save_error:
            print(f"❌ Failed to save audio file: {save_error}")
            return JsonResponse({
                "success": False,
                "error": "Failed to process audio file",
                "heard_input_query": "",
                "confidence_score": 0,
                "message": "Audio processing error. Please try again."
            }, status=500)
        
        # Convert audio to WAV format using pydub
        if PYDUB_AVAILABLE:
            try:
                print("🔄 Converting audio to WAV format...")
                
                # Load audio in any format (webm, mp4, etc.)
                audio = AudioSegment.from_file(temp_input_path)
                
                # Convert to WAV with proper settings for speech recognition
                audio = audio.set_frame_rate(16000)  # 16kHz sample rate
                audio = audio.set_channels(1)  # Mono
                audio = audio.set_sample_width(2)  # 16-bit
                
                # Export as WAV
                temp_wav_path = temp_input_path.replace('.webm', '.wav')
                audio.export(temp_wav_path, format='wav')
                print(f"✅ Converted to WAV: {temp_wav_path}")
                
            except Exception as convert_error:
                print(f"❌ Audio conversion failed: {convert_error}")
                print("💡 Make sure FFmpeg is installed: https://ffmpeg.org/download.html")
                return JsonResponse({
                    "success": False,
                    "error": f"Audio conversion failed: {str(convert_error)}",
                    "heard_input_query": "",
                    "confidence_score": 0,
                    "message": "Audio format conversion error. Please ensure FFmpeg is installed."
                }, status=500)
        else:
            print("❌ Pydub not available for audio conversion")
            return JsonResponse({
                "success": False,
                "error": "Audio conversion library not available",
                "heard_input_query": "",
                "confidence_score": 0,
                "message": "Server audio processing not configured. Please type your message."
            }, status=500)
        
        # Transcribe using Google Speech Recognition
        transcription = ""
        confidence_score = 0.0
        
        if SPEECH_RECOGNITION_AVAILABLE:
            try:
                recognizer = sr.Recognizer()
                
                # Use the converted WAV file
                with sr.AudioFile(temp_wav_path) as source:
                    # Adjust for ambient noise
                    recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = recognizer.record(source)
                
                # Use Google Speech Recognition (free tier)
                print(f"🎤 Transcribing audio with language: {language_code}")
                transcription = recognizer.recognize_google(audio, language=language_code)
                confidence_score = 0.9  # Google's free API doesn't return confidence
                
                print(f"✅ Transcription successful: '{transcription}'")
                
            except sr.UnknownValueError:
                print("⚠️ Could not understand audio")
                transcription = ""
                confidence_score = 0.0
            except sr.RequestError as e:
                print(f"❌ Google Speech Recognition service error: {e}")
                transcription = ""
                confidence_score = 0.0
            except Exception as transcribe_error:
                print(f"❌ Transcription error: {transcribe_error}")
                transcription = ""
                confidence_score = 0.0
        else:
            print("❌ Speech Recognition not available")
            return JsonResponse({
                "success": False,
                "error": "Speech recognition not available",
                "heard_input_query": "",
                "confidence_score": 0,
                "message": "Speech recognition is not configured. Please type your message."
            }, status=500)
        
        # Return transcription result
        if transcription and confidence_score > 0.7:
            return JsonResponse({
                "success": True,
                "heard_input_query": transcription,
                "confidence_score": confidence_score,
                "message": "Transcription successful",
                "error": False
            })
        else:
            return JsonResponse({
                "success": False,
                "heard_input_query": transcription or "",
                "confidence_score": confidence_score,
                "message": "Could not understand the audio clearly. Please speak louder and try again.",
                "error": True
            })
        
    except Exception as e:
        print(f"❌ Audio transcription error: {e}")
        logger.error(f"Audio transcription error: {e}", exc_info=True)
        
        return JsonResponse({
            "success": False,
            "error": str(e),
            "heard_input_query": "",
            "confidence_score": 0,
            "message": "Speech recognition temporarily unavailable. Please type your message."
        }, status=500)
    
    finally:
        # Clean up temp files
        for temp_path in [temp_input_path, temp_wav_path]:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                    print(f"🗑️ Cleaned up temp file: {temp_path}")
                except Exception as cleanup_error:
                    print(f"⚠️ Failed to cleanup temp file: {cleanup_error}")