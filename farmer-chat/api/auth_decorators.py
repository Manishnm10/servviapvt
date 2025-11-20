"""
Authentication & Authorization Decorators
Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): 2025-11-19 12:28:13
Current User's Login: Raghuraam21

Provides JWT-based authentication and role-based authorization
"""
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from functools import wraps
import logging
from database.models import User
from peewee import DoesNotExist

logger = logging.getLogger(__name__)


def jwt_required(view_func):
    """
    Decorator to require valid JWT token
    
    Extracts user from token and adds to request.jwt_user
    Returns 401 if token is invalid or missing
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({
                'success': False,
                'error': 'Authentication required. Please provide Bearer token.',
                'code': 'MISSING_TOKEN'
            }, status=401)
        
        token_str = auth_header.split(' ')[1]
        
        try:
            # Decode and validate token
            token = AccessToken(token_str)
            user_id = token.get('user_id')
            email = token.get('email')
            
            # Get user from database
            try:
                user = User.get(User.id == user_id)
                
                # Add user to request
                request.jwt_user = user
                
                logger.info(f"🔐 Authenticated user: {email} (role: {user.role})")
                
                return view_func(request, *args, **kwargs)
                
            except DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'User not found',
                    'code': 'USER_NOT_FOUND'
                }, status=401)
        
        except TokenError as e:
            return JsonResponse({
                'success': False,
                'error': 'Invalid or expired token',
                'code': 'INVALID_TOKEN',
                'details': str(e)
            }, status=401)
        
        except Exception as e:
            logger.error(f"Authentication error: {e}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': 'Authentication failed',
                'code': 'AUTH_ERROR'
            }, status=500)
    
    return wrapper


def patient_or_admin(view_func):
    """
    Decorator to allow access if:
    - User is accessing their own data (patient)
    - User is an admin
    
    Must be used AFTER @jwt_required
    Expects 'email' in request.GET or request data
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Ensure user is authenticated
        if not hasattr(request, 'jwt_user'):
            return JsonResponse({
                'success': False,
                'error': 'Authentication required',
                'code': 'NOT_AUTHENTICATED'
            }, status=401)
        
        user = request.jwt_user
        
        # Admin can access anything
        if user.role == 'admin':
            logger.info(f"🔓 Admin access granted: {user.email}")
            return view_func(request, *args, **kwargs)
        
        # Patient can only access their own data
        # Get email from request
        if request.method == 'GET':
            target_email = request.GET.get('email')
        else:
            import json
            try:
                data = json.loads(request.body) if request.body else {}
                target_email = data.get('email')
            except:
                target_email = None
        
        if not target_email:
            return JsonResponse({
                'success': False,
                'error': 'Email parameter required',
                'code': 'MISSING_EMAIL'
            }, status=400)
        
        # Check if user is accessing their own data
        if user.email.lower() == target_email.lower():
            logger.info(f"🔓 Patient accessing own data: {user.email}")
            return view_func(request, *args, **kwargs)
        else:
            logger.warning(f"🚫 Unauthorized access attempt: {user.email} tried to access {target_email}")
            return JsonResponse({
                'success': False,
                'error': 'Access denied. You can only access your own medical profile.',
                'code': 'PERMISSION_DENIED'
            }, status=403)
    
    return wrapper


def admin_only(view_func):
    """
    Decorator to restrict access to admin users only
    
    Must be used AFTER @jwt_required
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Ensure user is authenticated
        if not hasattr(request, 'jwt_user'):
            return JsonResponse({
                'success': False,
                'error': 'Authentication required',
                'code': 'NOT_AUTHENTICATED'
            }, status=401)
        
        user = request.jwt_user
        
        # Check if user is admin
        if user.role == 'admin':
            logger.info(f"🔓 Admin access granted: {user.email}")
            return view_func(request, *args, **kwargs)
        else:
            logger.warning(f"🚫 Admin access denied: {user.email} (role: {user.role})")
            return JsonResponse({
                'success': False,
                'error': 'Admin access required',
                'code': 'ADMIN_ONLY'
            }, status=403)
    
    return wrapper


def get_user_from_token(request):
    """
    Helper function to extract user from JWT token
    Returns (user, error_response)
    """
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return None, JsonResponse({
            'success': False,
            'error': 'Authentication required'
        }, status=401)
    
    token_str = auth_header.split(' ')[1]
    
    try:
        token = AccessToken(token_str)
        user_id = token.get('user_id')
        user = User.get(User.id == user_id)
        return user, None
    except:
        return None, JsonResponse({
            'success': False,
            'error': 'Invalid token'
        }, status=401)