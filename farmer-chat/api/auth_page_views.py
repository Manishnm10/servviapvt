"""
Authentication Page Views
Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): 2025-11-19 17:10:11
Current User's Login: Raghuraam21

Purpose:
- Serve HTML pages for login, registration, chatbot
- No authentication logic (that's in auth_views.py)
- Just renders templates
"""
from django.shortcuts import render
from django.http import HttpResponseRedirect
import logging

logger = logging.getLogger(__name__)


def index_page(request):
    """
    Serve the main chatbot page (index.html)
    
    GET /
    
    Returns:
        HTML: index.html template (chatbot interface)
    """
    logger.info("📄 Serving index/chatbot page")
    return render(request, 'index.html')


def login_page(request):
    """
    Serve the login page
    
    GET /login/
    
    Returns:
        HTML: login.html template
    """
    logger.info("📄 Serving login page")
    return render(request, 'auth/login.html')


def register_page(request):
    """
    Serve the registration page
    
    GET /register/
    
    Returns:
        HTML: register.html template
    """
    logger.info("📄 Serving registration page")
    return render(request, 'auth/register.html')


def dashboard_page(request):
    """
    Serve the user dashboard page
    (redirects to main chatbot - index.html)
    
    GET /dashboard/
    
    Returns:
        Redirect to index page (chatbot)
    """
    logger.info("📄 Dashboard accessed, redirecting to chatbot")
    return HttpResponseRedirect('/')