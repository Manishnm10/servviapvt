from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import ChatAPIViewSet, LanguageViewSet
from api.servvia_endpoint import get_answer_for_text_query
from api.language_endpoint import get_supported_languages
from api.audio_endpoint import transcribe_audio
from api.tts_endpoint import synthesise_audio  # 🔧 NEW IMPORT

# Create a router for the ViewSets
router = DefaultRouter()
router.register(r'chat', ChatAPIViewSet, basename='chat')
router.register(r'language', LanguageViewSet, basename='language')

urlpatterns = [
    # Include ViewSet routes (this will handle synthesise_audio and other ViewSet methods)
    path('', include(router.urls)),
    
    # ServVIA Healthcare endpoints (function-based views)
    path("chat/get_answer_for_text_query/", get_answer_for_text_query, name="servvia-healthcare"),
    path("api/chat/get_answer_for_text_query/", get_answer_for_text_query, name="servvia-healthcare-double-api"),
    
    # 🔧 NEW: TTS endpoints (function-based view - no authentication required)
    path("chat/synthesise_audio/", synthesise_audio, name="synthesise-audio"),
    path("api/chat/synthesise_audio/", synthesise_audio, name="synthesise-audio-double-api"),
    
    # Language endpoints (function-based views)
    path("languages/", get_supported_languages, name="get-languages"),
    path("language/languages/", get_supported_languages, name="get-languages-alt"),
    path("api/language/languages/", get_supported_languages, name="get-languages-double-api"),
    
    # Audio transcription endpoint (function-based view)
    path("api/chat/transcribe_audio/", transcribe_audio, name="transcribe-audio"),
    path("chat/transcribe_audio/", transcribe_audio, name="transcribe-audio-single"),
]