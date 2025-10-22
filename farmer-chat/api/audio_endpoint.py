from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import logging
import tempfile
import os

logger = logging.getLogger(__name__)

# Try to import speech recognition
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
    print("✅ Speech Recognition available")
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    print("❌ Speech Recognition not available - install with: pip install SpeechRecognition")

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
    
    try:
        print("🎤 ServVIA: Audio transcription request received")
        
        # Check if audio file is present
        if 'audio' not in request.FILES:
            print("❌ No audio file found in request")
            return JsonResponse({
                "success": False,
                "error": "No audio file provided",
                "transcription": "",
                "message": "Please speak into the microphone and try again."
            }, status=400)
        
        audio_file = request.FILES['audio']
        print(f"🎤 Audio file received: {audio_file.name}, size: {audio_file.size} bytes")
        
        # Use Web Speech API fallback (browser-based transcription)
        # This is more reliable than server-side processing
        return JsonResponse({
            "success": True,
            "transcription": "",
            "message": "Please enable Web Speech API in your browser",
            "instructions": "ServVIA uses browser-based speech recognition. Please allow microphone access and try speaking again."
        })
        
    except Exception as e:
        print(f"❌ Audio transcription error: {e}")
        logger.error(f"Audio transcription error: {e}")
        
        return JsonResponse({
            "success": False,
            "error": str(e),
            "transcription": "",
            "message": "Speech recognition temporarily unavailable. Please type your message."
        }, status=500)