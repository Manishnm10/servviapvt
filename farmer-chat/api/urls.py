from django.urls import path
from api.servvia_endpoint import get_answer_for_text_query
from api.language_endpoint import get_supported_languages
from api.audio_endpoint import transcribe_audio

urlpatterns = [
    # ServVIA Healthcare endpoints
    path("chat/get_answer_for_text_query/", get_answer_for_text_query, name="servvia-healthcare"),
    path("api/chat/get_answer_for_text_query/", get_answer_for_text_query, name="servvia-healthcare-double-api"),
    
    # Language endpoints
    path("languages/", get_supported_languages, name="get-languages"),
    path("language/languages/", get_supported_languages, name="get-languages-alt"),
    path("api/language/languages/", get_supported_languages, name="get-languages-double-api"),
    
    # Audio transcription endpoint
    path("api/chat/transcribe_audio/", transcribe_audio, name="transcribe-audio"),
    path("chat/transcribe_audio/", transcribe_audio, name="transcribe-audio-single"),
]