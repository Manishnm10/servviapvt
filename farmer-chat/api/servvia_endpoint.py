from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import asyncio

try:
    from language_service.translation import (
        detect_language_and_translate_to_english,
        translate_text_to_language,
    )
except ImportError:
    detect_language_and_translate_to_english = None
    translate_text_to_language = None

@csrf_exempt
def get_answer_for_text_query(request):
    """
    Automatically detect the language of the user's query and respond in the same language.
    """
    if request.method == "POST":
        try:
            # Parse request data
            data = json.loads(request.body) if request.body else {}
            original_query = data.get("message", "")
            email = data.get("email", "user@servvia.com")
            
            # Default to English if detection fails
            detected_language = "en"
            english_query = original_query

            # Step 1: Detect user's language and translate query to English
            if detect_language_and_translate_to_english:
                english_query, detected_language = asyncio.run(
                    detect_language_and_translate_to_english(original_query)
                )

            # Step 2: Generate response (in English)
            response = f"Processed query: {english_query}"

            # Step 3: Translate response back to detected language
            if translate_text_to_language and detected_language != "en":
                response = asyncio.run(
                    translate_text_to_language(response, detected_language)
                )

            # Return response in detected language
            return JsonResponse({
                "message": response,
                "language": detected_language,
                "original_query": original_query,
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid method"}, status=405)