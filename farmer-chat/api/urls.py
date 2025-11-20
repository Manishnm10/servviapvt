"""
API URL Configuration
Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): 2025-11-19 17:12:48
Current User's Login: Raghuraam21

Includes:
- HTML Page Routes (Login, Register, Chatbot)
- Chat API (ServVIA Healthcare)
- Authentication APIs (JWT + OAuth)
- Medical Profile APIs (AES-256 Encrypted)
- Language services
- Audio transcription
- Text-to-Speech (TTS)

IMPORTANT: HTML page routes MUST come FIRST before API routes
to avoid routing conflicts where ViewSets intercept page requests.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import ChatAPIViewSet, LanguageViewSet
from api.servvia_endpoint import get_answer_for_text_query
from api.language_endpoint import get_supported_languages
from api.audio_endpoint import transcribe_audio
from api.tts_endpoint import synthesise_audio

from api.auth_page_views import (
    index_page,
    login_page, 
    register_page, 
    dashboard_page
)

from api.medical_profile_api import (
    create_or_update_medical_profile,
    get_medical_profile,
    delete_medical_profile_endpoint,
    get_profile_history,
    update_consent
)

from api.auth_views import (
    login_view,
    register_view,
    token_refresh_view,
    logout_view,
    verify_token_view
)

from api.google_oauth import (
    google_login_initiate,
    google_oauth_callback,
    google_oauth_status
)

# Create a router for the ViewSets
router = DefaultRouter()
router.register(r'chat', ChatAPIViewSet, basename='chat')
router.register(r'language', LanguageViewSet, basename='language')

urlpatterns = [
    # ============================================================
    # HTML PAGE ROUTES (MUST BE FIRST!)
    # Current Date and Time (UTC): 2025-11-19 17:12:48
    # Current User: Raghuraam21
    # ============================================================
    # Main chatbot page (requires authentication)
    #path("", index_page, name="chatbot-home"),
    
    # Authentication pages
    #path("login/", login_page, name="login-page"),
    #path("register/", register_page, name="register-page"),
    #path("dashboard/", dashboard_page, name="dashboard-page"),
    
    # ============================================================
    # AUTHENTICATION API ENDPOINTS
    # ============================================================
    # User login (bcrypt password verification)
    path("auth/login/", login_view, name="auth-login"),

    # User registration (bcrypt password hashing)
    path("auth/register/", register_view, name="auth-register"),

    # Refresh access token
    path("auth/token/refresh/", token_refresh_view, name="auth-token-refresh"),

    # Logout (blacklist token)
    path("auth/logout/", logout_view, name="auth-logout"),

    # Verify token
    path("auth/token/verify/", verify_token_view, name="auth-token-verify"),
    
    # ============================================================
    # GOOGLE OAUTH ENDPOINTS 
    # ============================================================
    # Initiate Google OAuth login
    path("auth/google/login/", google_login_initiate, name="google-oauth-login"),

    # Google OAuth callback (after user authorizes) 
    path("auth/google/callback/", google_oauth_callback, name="google-oauth-callback"),

    # Check OAuth configuration status
    path("auth/google/status/", google_oauth_status, name="google-oauth-status"),

    # ============================================================
    # MEDICAL PROFILE API ENDPOINTS (AES-256 Encrypted)
    # ============================================================
    # Create or update medical profile
    path("medical/profile/",
         create_or_update_medical_profile,
         name="medical-profile-create-update"),

    # Get medical profile
    path("medical/profile/get/",
         get_medical_profile,
         name="medical-profile-get"),

    # Delete medical profile
    path("medical/profile/delete/",
         delete_medical_profile_endpoint,
         name="medical-profile-delete"),

    # Get profile history (audit log)
    path("medical/history/",
         get_profile_history,
         name="medical-profile-history"),

    # Update consent
    path("medical/consent/",
         update_consent,
         name="medical-consent"),
    
    # ============================================================
    # SERVVIA HEALTHCARE CHAT ENDPOINTS (PRIORITY ROUTES)
    # ============================================================
    # CRITICAL: These MUST come BEFORE ViewSet routes
    # Otherwise the ViewSet router will intercept the requests
    
    # Main chat endpoint
    path("chat/get_answer_for_text_query/", 
         get_answer_for_text_query, 
         name="servvia-healthcare"),
    
    # Modern REST API path for healthcare queries
    path("servvia/healthcare/",
         get_answer_for_text_query,
         name="servvia-healthcare-rest"),
    
    # Alternative with double 'api' prefix
    path("api/chat/get_answer_for_text_query/", 
         get_answer_for_text_query, 
         name="servvia-healthcare-double-api"),
    
    # ============================================================
    # TEXT-TO-SPEECH (TTS) ENDPOINTS
    # ============================================================
    # Main TTS endpoint (no authentication required)
    path("chat/synthesise_audio/", 
         synthesise_audio, 
         name="synthesise-audio"),
    
    # Alternative with double 'api' prefix
    path("api/chat/synthesise_audio/", 
         synthesise_audio, 
         name="synthesise-audio-double-api"),
    
    # ============================================================
    # AUDIO TRANSCRIPTION ENDPOINTS
    # ============================================================
    # Audio to text transcription
    path("api/chat/transcribe_audio/", 
         transcribe_audio, 
         name="transcribe-audio"),
    
    path("chat/transcribe_audio/", 
         transcribe_audio, 
         name="transcribe-audio-single"),
    
    # ============================================================
    # LANGUAGE SERVICE ENDPOINTS
    # ============================================================
    # Get supported languages
    path("languages/", 
         get_supported_languages, 
         name="get-languages"),
    
    path("language/languages/", 
         get_supported_languages, 
         name="get-languages-alt"),
    
    path("api/language/languages/", 
         get_supported_languages, 
         name="get-languages-double-api"),
    
    # ============================================================
    # VIEWSET ROUTES (Chat & Language ViewSets)
    # ============================================================
    # IMPORTANT: This MUST come AFTER all specific routes above
    # The ViewSet router creates catch-all patterns that will
    # intercept requests if placed first
    path('', include(router.urls)),
    
    # ============================================================
    # 🗄️ ARCHIVED: SKIN DISEASE CLASSIFICATION (Medical AI)
    # ============================================================
    # NOTE: Healthcare module moved to _archived_local_pdf_processing/
    # Now using remote FarmStack API for healthcare content
    # Uncomment these lines if you restore the healthcare module
    
    # Skin disease prediction endpoints (COMMENTED OUT)
    # path('healthcare/skin-disease/', 
    #      include('healthcare.skin_classifier.urls')),
    
    # Alternative with 'api' prefix for consistency (COMMENTED OUT)
    # path('api/healthcare/skin-disease/', 
    #      include('healthcare.skin_classifier.urls')),
]