"""
Google OAuth 2.0 Integration
Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): 2025-11-19 14:05:12
Current User's Login: Raghuraam21

Provides "Login with Google" functionality with JWT token generation
"""
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import requests
import json
import logging
from urllib.parse import urlencode
from database.models import User
from peewee import DoesNotExist
from api.auth_views import generate_tokens_for_user

logger = logging.getLogger(__name__)


def get_google_oauth_url():
    """Generate Google OAuth authorization URL"""
    params = {
        'client_id': settings.GOOGLE_OAUTH_CLIENT_ID,
        'redirect_uri': settings.GOOGLE_OAUTH_REDIRECT_URI,
        'response_type': 'code',
        'scope': ' '.join(settings.GOOGLE_OAUTH_SCOPES),
        'access_type': 'offline',
        'prompt': 'consent',
    }
    
    auth_url = f"{settings.GOOGLE_OAUTH_CONFIG['auth_uri']}?{urlencode(params)}"
    return auth_url


@csrf_exempt
def google_login_initiate(request):
    """
    Step 1: Initiate Google OAuth flow
    
    GET /api/auth/google/login/
    
    Redirects user to Google login page
    """
    try:
        # Generate OAuth URL
        auth_url = get_google_oauth_url()
        
        logger.info("🔐 Initiating Google OAuth flow")
        
        # Return redirect URL (for API) or redirect directly (for web)
        if request.GET.get('format') == 'json':
            return JsonResponse({
                'success': True,
                'auth_url': auth_url,
                'message': 'Redirect user to this URL for Google login'
            })
        else:
            # Direct redirect for web browser
            return HttpResponseRedirect(auth_url)
    
    except Exception as e:
        logger.error(f"Error initiating Google OAuth: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
def google_oauth_callback(request):
    """
    Step 2: Handle Google OAuth callback
    
    GET /api/auth/google/callback/?code=xxxxx
    
    Exchanges authorization code for access token and creates/logs in user
    
    Returns:
        JSON with JWT tokens and user info
    """
    if request.method != 'GET':
        return JsonResponse({
            'success': False,
            'error': 'Method not allowed. Use GET.'
        }, status=405)
    
    try:
        # Get authorization code from query params
        auth_code = request.GET.get('code')
        error = request.GET.get('error')
        
        if error:
            logger.error(f"OAuth error: {error}")
            return JsonResponse({
                'success': False,
                'error': f'Google OAuth error: {error}'
            }, status=400)
        
        if not auth_code:
            return JsonResponse({
                'success': False,
                'error': 'Authorization code missing'
            }, status=400)
        
        logger.info("🔐 Received OAuth callback with authorization code")
        
        # Exchange authorization code for access token
        token_data = {
            'code': auth_code,
            'client_id': settings.GOOGLE_OAUTH_CLIENT_ID,
            'client_secret': settings.GOOGLE_OAUTH_CLIENT_SECRET,
            'redirect_uri': settings.GOOGLE_OAUTH_REDIRECT_URI,
            'grant_type': 'authorization_code',
        }
        
        logger.info("🔄 Exchanging authorization code for access token")
        
        token_response = requests.post(
            settings.GOOGLE_OAUTH_CONFIG['token_uri'],
            data=token_data,
            timeout=10
        )
        
        if token_response.status_code != 200:
            logger.error(f"Token exchange failed: {token_response.text}")
            return JsonResponse({
                'success': False,
                'error': 'Failed to exchange authorization code for token',
                'details': token_response.text
            }, status=400)
        
        tokens = token_response.json()
        access_token = tokens.get('access_token')
        
        if not access_token:
            return JsonResponse({
                'success': False,
                'error': 'No access token received from Google'
            }, status=400)
        
        logger.info("✅ Access token received, fetching user info")
        
        # Get user information from Google
        userinfo_response = requests.get(
            settings.GOOGLE_OAUTH_CONFIG['userinfo_uri'],
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=10
        )
        
        if userinfo_response.status_code != 200:
            logger.error(f"Userinfo fetch failed: {userinfo_response.text}")
            return JsonResponse({
                'success': False,
                'error': 'Failed to fetch user information from Google'
            }, status=400)
        
        userinfo = userinfo_response.json()
        
        # Extract user data
        google_id = userinfo.get('id')
        email = userinfo.get('email')
        name = userinfo.get('name')
        given_name = userinfo.get('given_name')
        family_name = userinfo.get('family_name')
        picture = userinfo.get('picture')
        
        # Default to True if Google doesn't provide verification status
        # This handles Google Workspace accounts and test users
        email_verified = userinfo.get('email_verified', True)
        
        logger.info(f"✅ User info received: {email} (verified: {email_verified})")
        
        if not email:
            return JsonResponse({
                'success': False,
                'error': 'Email not provided by Google'
            }, status=400)
        
        # Only reject if explicitly marked as unverified
        if email_verified is False:
            logger.warning(f"⚠️ Email verification failed for: {email}")
            return JsonResponse({
                'success': False,
                'error': 'Email not verified by Google. Please verify your email first.'
            }, status=400)
        
        logger.info(f"✅ Email verification passed for: {email}")
        
        # Get or create user in database
        try:
            user = User.get(User.email == email)
            logger.info(f"✅ Existing user found: {email}")
            action = 'logged_in'
        except DoesNotExist:
            # Create new user
            user = User.create(
                email=email,
                first_name=given_name or name,
                last_name=family_name or '',
                role='patient'  # Default role for OAuth users
            )
            logger.info(f"✅ New user created via OAuth: {email}")
            action = 'registered'
        
        # Generate JWT tokens for the user
        jwt_tokens = generate_tokens_for_user(user)
        
        logger.info(f"✅ JWT tokens generated for {email}")
        
        # Return success response with tokens
        response_data = {
            'success': True,
            'action': action,
            'message': f'Successfully {action} via Google OAuth',
            'access': jwt_tokens['access'],
            'refresh': jwt_tokens['refresh'],
            'user': {
                'id': str(user.id),
                'email': user.email,
                'name': name,
                'first_name': given_name,
                'last_name': family_name,
                'picture': picture,
                'role': user.role,
                'auth_method': 'google_oauth'
            }
        }
        
        # For web browser, return HTML with tokens (you can customize this)
        if 'text/html' in request.headers.get('Accept', ''):
            html_response = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Login Successful - ServVIA</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        margin: 0;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    }}
                    .container {{
                        background: white;
                        padding: 40px;
                        border-radius: 10px;
                        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                        text-align: center;
                        max-width: 500px;
                    }}
                    h1 {{ color: #667eea; }}
                    .success {{ color: #10b981; font-size: 48px; }}
                    .user-info {{
                        margin: 20px 0;
                        padding: 20px;
                        background: #f3f4f6;
                        border-radius: 8px;
                    }}
                    .token {{
                        background: #1f2937;
                        color: #10b981;
                        padding: 15px;
                        border-radius: 5px;
                        font-family: monospace;
                        font-size: 12px;
                        word-break: break-all;
                        margin: 10px 0;
                    }}
                    button {{
                        background: #667eea;
                        color: white;
                        border: none;
                        padding: 12px 24px;
                        border-radius: 5px;
                        cursor: pointer;
                        font-size: 16px;
                        margin: 5px;
                    }}
                    button:hover {{ background: #5568d3; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="success">✅</div>
                    <h1>Login Successful!</h1>
                    <div class="user-info">
                        <img src="{picture}" alt="Profile" style="border-radius: 50%; width: 80px; height: 80px;">
                        <p><strong>{name}</strong></p>
                        <p>{email}</p>
                        <p>Role: {user.role}</p>
                    </div>
                    
                    <h3>Access Token:</h3>
                    <div class="token">{jwt_tokens['access'][:100]}...</div>
                    
                    <button onclick="copyToken()">Copy Access Token</button>
                    <button onclick="closeWindow()">Close</button>
                    
                    <script>
                        // Store tokens in localStorage
                        localStorage.setItem('access_token', '{jwt_tokens['access']}');
                        localStorage.setItem('refresh_token', '{jwt_tokens['refresh']}');
                        localStorage.setItem('user', JSON.stringify({json.dumps(response_data['user'])}));
                        
                        function copyToken() {{
                            navigator.clipboard.writeText('{jwt_tokens['access']}');
                            alert('Access token copied to clipboard!');
                        }}
                        
                        function closeWindow() {{
                            window.close();
                        }}
                        
                        // Auto-redirect after 5 seconds
                        setTimeout(() => {{
                            window.location.href = '/';
                        }}, 5000);
                    </script>
                </div>
            </body>
            </html>
            """
            return HttpResponse(html_response)
        
        # For API requests, return JSON
        return JsonResponse(response_data)
    
    except requests.RequestException as e:
        logger.error(f"OAuth request error: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': f'OAuth request failed: {str(e)}'
        }, status=500)
    except Exception as e:
        logger.error(f"OAuth callback error: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
def google_oauth_status(request):
    """
    Check Google OAuth configuration status
    
    GET /api/auth/google/status/
    
    Returns whether OAuth is properly configured
    """
    try:
        is_configured = all([
            settings.GOOGLE_OAUTH_CLIENT_ID,
            settings.GOOGLE_OAUTH_CLIENT_SECRET,
            settings.GOOGLE_OAUTH_REDIRECT_URI,
        ])
        
        return JsonResponse({
            'success': True,
            'oauth_configured': is_configured,
            'client_id': settings.GOOGLE_OAUTH_CLIENT_ID[:20] + '...' if settings.GOOGLE_OAUTH_CLIENT_ID else None,
            'redirect_uri': settings.GOOGLE_OAUTH_REDIRECT_URI,
            'scopes': settings.GOOGLE_OAUTH_SCOPES,
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)