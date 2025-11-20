"""
Main Project URL Configuration
Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): 2025-11-19 17:15:36
Current User's Login: Raghuraam21
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Import page views directly
from api.auth_page_views import index_page, login_page, register_page, dashboard_page

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    
    # HTML Page Routes (NO api/ prefix)
    path('', index_page, name='chatbot-home'),
    path('login/', login_page, name='login-page'),
    path('register/', register_page, name='register-page'),
    path('dashboard/', dashboard_page, name='dashboard-page'),
    
    # API Routes (WITH api/ prefix)
    path('api/', include('api.urls')),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)