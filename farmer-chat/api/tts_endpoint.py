from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import logging

logger = logging.getLogger(__name__)

# Import the TTS processing function
from api.utils import process_output_audio

@csrf_exempt
def synthesise_audio(request):
    """
    ServVIA TTS endpoint - Generate audio from text without authentication requirements
    """
    
    # Handle OPTIONS request (CORS preflight)
    if request.method == "OPTIONS":
        response = JsonResponse({})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type"
        return response
    
    # Handle POST request
    if request.method == "POST":
        try:
            # Parse POST request data
            if request.content_type == 'application/json':
                data = json.loads(request.body) if request.body else {}
            else:
                data = dict(request.POST)
            
            # Extract text and message_id from request
            original_text = data.get('text', '')
            message_id = data.get('message_id', None)
            email_id = data.get('email_id', 'user@servvia.com')
            
            # Handle list values (from form data)
            if isinstance(original_text, list):
                original_text = original_text[0] if original_text else ''
            if isinstance(message_id, list):
                message_id = message_id[0] if message_id else None
            if isinstance(email_id, list):
                email_id = email_id[0] if email_id else 'user@servvia.com'
            
            print(f"🔊 ServVIA TTS: Processing text for audio synthesis")
            logger.info(f"🔊 ServVIA TTS: Processing '{original_text[:50]}...'")
            
            if not original_text or not str(original_text).strip():
                return JsonResponse({
                    "success": False,
                    "error": True,
                    "message": "Please submit text for audio synthesis.",
                    "audio": None
                }, status=400)

            # Process the text to audio
            print(f"🔊 Processing TTS for: '{original_text[:50]}...'")
            response_audio = process_output_audio(original_text, message_id)

            if not response_audio:
                logger.error("❌ Failed to generate audio - response_audio is None")
                return JsonResponse({
                    "success": False,
                    "error": True,
                    "message": "Unable to generate audio currently. Please try again.",
                    "audio": None
                }, status=500)

            print(f"✅ ServVIA TTS: Audio synthesis successful")
            logger.info("✅ Audio synthesis successful")
            
            return JsonResponse({
                "success": True,
                "error": False,
                "text": original_text,
                "audio": response_audio,
                "message": "Audio synthesis successful"
            })
                
        except Exception as e:
            print(f"❌ ServVIA TTS Error: {e}")
            logger.error(f"ServVIA TTS Error: {e}", exc_info=True)
            return JsonResponse({
                "success": False,
                "error": True,
                "message": f"Something went wrong: {str(e)}",
                "audio": None
            }, status=500)
    
    # Handle other methods
    return JsonResponse({
        "error": "Method not allowed",
        "allowed_methods": ["POST", "OPTIONS"]
    }, status=405)