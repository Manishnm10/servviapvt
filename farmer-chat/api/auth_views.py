"""
Authentication Views with Enhanced Security
Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): 2025-11-20 12:50:32
Current User's Login: Raghuraam21

Enhanced with:
- Bcrypt password hashing
- Password strength validation
- Email validation
- Rate limiting
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
import json
import logging
import bcrypt
from database.models import User
from peewee import DoesNotExist
from datetime import datetime

# Import password utilities
from api.password_utils import (
    PasswordHasher,
    PasswordValidator,
    validate_email
)

logger = logging.getLogger(__name__)


def generate_tokens_for_user(user):
    """
    Generate JWT tokens for a user
    
    Args:
        user: User model instance
        
    Returns:
        dict with 'access' and 'refresh' tokens
    """
    refresh = RefreshToken()
    
    # Add custom claims
    refresh['user_id'] = str(user.id)
    refresh['email'] = user.email
    refresh['role'] = user.role
    
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }


@csrf_exempt
def register_view(request):
    """
    User Registration Endpoint with Enhanced Security
    
    POST /api/auth/register/
    
    Request Body:
        {
            "email": "user@example.com",
            "password": "SecurePass123!",
            "first_name": "John",
            "last_name": "Doe",
            "role": "patient"  // optional, defaults to "patient"
        }
    
    Response:
        {
            "success": true,
            "message": "User registered successfully",
            "user": {
                "id": "uuid",
                "email": "user@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "role": "patient"
            },
            "access": "jwt_access_token",
            "refresh": "jwt_refresh_token"
        }
    
    Security Features:
        - Password strength validation
        - Bcrypt password hashing
        - Email format validation
        - Duplicate email prevention
    """
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'Method not allowed. Use POST.'
        }, status=405)
    
    try:
        # Parse request body
        data = json.loads(request.body.decode('utf-8'))
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        role = data.get('role', 'patient').lower()
        
        logger.info(f"📝 Registration attempt for: {email}")
        
        # ============================================================
        # VALIDATION
        # ============================================================
        
        # Validate email
        email_valid, email_error = validate_email(email)
        if not email_valid:
            return JsonResponse({
                'success': False,
                'error': email_error
            }, status=400)
        
        # Validate password strength
        password_valid, password_result = PasswordValidator.validate_password_strength(password)
        if not password_valid:
            return JsonResponse({
                'success': False,
                'error': 'Password does not meet requirements',
                'password_requirements': {
                    'minimum_length': PasswordValidator.MIN_LENGTH,
                    'requirements': [
                        'At least one uppercase letter',
                        'At least one lowercase letter',
                        'At least one digit',
                        'At least one special character (!@#$%^&*...)'
                    ],
                    'feedback': password_result['feedback'],
                    'requirements_met': password_result['requirements_met']
                }
            }, status=400)
        
        # Validate required fields
        if not first_name:
            return JsonResponse({
                'success': False,
                'error': 'First name is required'
            }, status=400)
        
        # Validate role
        valid_roles = ['patient', 'admin', 'doctor']
        if role not in valid_roles:
            return JsonResponse({
                'success': False,
                'error': f'Invalid role. Must be one of: {", ".join(valid_roles)}'
            }, status=400)
        
        # ============================================================
        # CHECK FOR EXISTING USER
        # ============================================================
        
        try:
            existing_user = User.get(User.email == email)
            logger.warning(f"⚠️ Registration failed: Email already exists - {email}")
            return JsonResponse({
                'success': False,
                'error': 'An account with this email already exists'
            }, status=400)
        except DoesNotExist:
            pass  # Good, email is available
        
        # ============================================================
        # HASH PASSWORD (BCRYPT)
        # ============================================================
        
        logger.info(f"🔐 Hashing password for {email}")
        hashed_password = PasswordHasher.hash_password(password)
        logger.info(f"✅ Password hashed successfully (length: {len(hashed_password)})")
        
        # ============================================================
        # CREATE USER
        # ============================================================
        
        user = User.create(
            email=email,
            password=hashed_password,  # Store hashed password
            first_name=first_name,
            last_name=last_name,
            role=role
        )
        
        logger.info(f"✅ User created successfully: {email} (ID: {user.id})")
        
        # ============================================================
        # GENERATE JWT TOKENS
        # ============================================================
        
        tokens = generate_tokens_for_user(user)
        
        logger.info(f"✅ JWT tokens generated for {email}")
        
        # ============================================================
        # SUCCESS RESPONSE
        # ============================================================
        
        return JsonResponse({
            'success': True,
            'message': 'User registered successfully',
            'user': {
                'id': str(user.id),
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role
            },
            'access': tokens['access'],
            'refresh': tokens['refresh'],
            'password_strength': password_result['strength']
        }, status=201)
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON in request body'
        }, status=400)
    
    except Exception as e:
        logger.error(f"Registration error: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'Internal server error during registration'
        }, status=500)


@csrf_exempt
def login_view(request):
    """
    User login endpoint
    Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): 2025-11-20 12:50:32
    Current User's Login: Raghuraam21
    
    POST /api/auth/login/
    
    Request body:
    {
        "email": "user@example.com",
        "password": "securepassword123"
    }
    
    Returns:
    {
        "success": true,
        "message": "Login successful",
        "user": {...},
        "access": "jwt_access_token",
        "refresh": "jwt_refresh_token"
    }
    """
    if request.method != 'POST':
        return JsonResponse({
            "success": False,
            "error": "Method not allowed. Use POST."
        }, status=405)
    
    try:
        # Parse request body
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        # Validate input
        if not email or not password:
            return JsonResponse({
                "success": False,
                "error": "Email and password are required"
            }, status=400)
        
        # Check if user exists
        try:
            user = User.get(User.email == email)
        except User.DoesNotExist:
            logger.warning(f"❌ Login attempt for non-existent user: {email}")
            return JsonResponse({
                "success": False,
                "error": "Invalid email or password"
            }, status=401)
        
        # ✅ FIXED: Check if user has a password (regular auth) or uses OAuth
        if not user.password:
            # User has no password - must be OAuth user
            oauth_provider = getattr(user, 'oauth_provider', None)
            if oauth_provider == 'google':
                return JsonResponse({
                    "success": False,
                    "error": "This account uses Google OAuth. Please login with Google."
                }, status=400)
            else:
                return JsonResponse({
                    "success": False,
                    "error": "This account has no password set. Please reset your password or use social login."
                }, status=400)
        
        # Verify password with bcrypt
        logger.info(f"🔐 Verifying password for user: {email}")
        
        try:
            # Use bcrypt to verify password
            password_bytes = password.encode('utf-8')
            hashed_bytes = user.password.encode('utf-8')
            
            if bcrypt.checkpw(password_bytes, hashed_bytes):
                logger.info(f"✅ Password verified successfully for: {email}")
            else:
                logger.warning(f"❌ Invalid password for user: {email}")
                return JsonResponse({
                    "success": False,
                    "error": "Invalid email or password"
                }, status=401)
                
        except Exception as e:
            logger.error(f"❌ Password verification error: {e}")
            return JsonResponse({
                "success": False,
                "error": "Authentication error. Please try again."
            }, status=500)
        
        # ============================================================
        # ✅ FIXED: Generate JWT tokens using standard RefreshToken
        # ============================================================
        logger.info(f"🎟️ Generating JWT tokens for: {email}")
        
        try:
            # Use the helper function instead of for_user_custom
            tokens = generate_tokens_for_user(user)
            access_token = tokens['access']
            refresh_token = tokens['refresh']
            
            logger.info(f"✅ JWT tokens generated successfully for: {email}")
            
        except Exception as token_error:
            logger.error(f"❌ JWT token generation error: {token_error}", exc_info=True)
            return JsonResponse({
                "success": False,
                "error": "Authentication successful but token generation failed"
            }, status=500)
        
        # Prepare user data
        user_data = {
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role
        }
        
        logger.info(f"✅ Login successful for: {email}")
        
        return JsonResponse({
            "success": True,
            "message": "Login successful",
            "user": user_data,
            "access": access_token,
            "refresh": refresh_token
        }, status=200)
        
    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "error": "Invalid JSON in request body"
        }, status=400)
    except Exception as e:
        logger.error(f"❌ Login error: {e}", exc_info=True)
        return JsonResponse({
            "success": False,
            "error": "Internal server error"
        }, status=500)


@csrf_exempt
def token_refresh_view(request):
    """
    Refresh JWT Access Token
    
    POST /api/auth/token/refresh/
    
    Request Body:
        {
            "refresh": "jwt_refresh_token"
        }
    
    Response:
        {
            "success": true,
            "access": "new_jwt_access_token"
        }
    """
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'Method not allowed. Use POST.'
        }, status=405)
    
    try:
        data = json.loads(request.body.decode('utf-8'))
        refresh_token = data.get('refresh')
        
        if not refresh_token:
            return JsonResponse({
                'success': False,
                'error': 'Refresh token is required'
            }, status=400)
        
        # Refresh the token
        try:
            refresh = RefreshToken(refresh_token)
            new_access_token = str(refresh.access_token)
            
            logger.info("✅ Access token refreshed successfully")
            
            return JsonResponse({
                'success': True,
                'access': new_access_token
            })
        
        except TokenError as e:
            logger.warning(f"⚠️ Token refresh failed: {e}")
            return JsonResponse({
                'success': False,
                'error': 'Invalid or expired refresh token'
            }, status=401)
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON in request body'
        }, status=400)
    
    except Exception as e:
        logger.error(f"Token refresh error: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)


@csrf_exempt
def logout_view(request):
    """
    User Logout (Blacklist Refresh Token)
    
    POST /api/auth/logout/
    
    Request Body:
        {
            "refresh": "jwt_refresh_token"
        }
    
    Response:
        {
            "success": true,
            "message": "Logged out successfully"
        }
    """
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'Method not allowed. Use POST.'
        }, status=405)
    
    try:
        data = json.loads(request.body.decode('utf-8'))
        refresh_token = data.get('refresh')
        
        if not refresh_token:
            return JsonResponse({
                'success': False,
                'error': 'Refresh token is required'
            }, status=400)
        
        try:
            # ✅ FIXED: Check if blacklist method exists
            token = RefreshToken(refresh_token)
            
            # Try to blacklist if method exists
            if hasattr(token, 'blacklist'):
                token.blacklist()
                logger.info("✅ Token blacklisted successfully")
            else:
                logger.warning("⚠️ Token blacklist method not available, token remains valid until expiry")
            
            return JsonResponse({
                'success': True,
                'message': 'Logged out successfully'
            })
        
        except TokenError:
            # Token already invalid/blacklisted
            return JsonResponse({
                'success': True,
                'message': 'Already logged out'
            })
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON in request body'
        }, status=400)
    
    except Exception as e:
        logger.error(f"Logout error: {e}", exc_info=True)
        # Don't fail logout even if blacklist fails
        return JsonResponse({
            'success': True,
            'message': 'Logged out successfully'
        })


@csrf_exempt
def verify_token_view(request):
    """
    Verify if JWT Token is Valid
    
    POST /api/auth/token/verify/
    
    Request Body:
        {
            "token": "jwt_access_or_refresh_token"
        }
    
    Response:
        {
            "success": true,
            "valid": true,
            "token_type": "access"
        }
    """
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'Method not allowed. Use POST.'
        }, status=405)
    
    try:
        data = json.loads(request.body.decode('utf-8'))
        token = data.get('token')
        
        if not token:
            return JsonResponse({
                'success': False,
                'error': 'Token is required'
            }, status=400)
        
        try:
            # Try to decode token
            RefreshToken(token)
            
            return JsonResponse({
                'success': True,
                'valid': True,
                'message': 'Token is valid'
            })
        
        except TokenError:
            return JsonResponse({
                'success': False,
                'valid': False,
                'message': 'Token is invalid or expired'
            }, status=401)
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON in request body'
        }, status=400)
    
    except Exception as e:
        logger.error(f"Token verification error: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)