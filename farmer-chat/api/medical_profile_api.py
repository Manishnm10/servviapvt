"""
Medical Profile REST API Endpoints
Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): 2025-11-19 12:36:57
Current User's Login: Raghuraam21

Provides CRUD operations for user medical profiles with:
- HIPAA-compliant audit logging
- Encrypted storage
- Request validation
- JWT Authentication (NEW!)
- Role-based access control (NEW!)
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import logging
from datetime import datetime

# Import authentication decorators
from api.auth_decorators import jwt_required, patient_or_admin, admin_only

logger = logging.getLogger(__name__)

# Import medical profile operations with aliases
try:
    from medical.medical_db_operations import (
        create_medical_profile as db_create_profile,
        get_medical_profile_by_user_id as db_get_profile,
        update_medical_profile as db_update_profile,
        delete_medical_profile as db_delete_profile,
        get_medical_profile_history as db_get_history
    )
    MEDICAL_DB_AVAILABLE = True
    logger.info("✅ Medical DB operations loaded successfully")
except ImportError as e:
    MEDICAL_DB_AVAILABLE = False
    logger.error(f"❌ Medical DB operations not available: {e}")

# Import user operations
try:
    from database.models import User
    from database.database_config import db_conn
    from common.utils import get_or_create_user_by_email
    USER_MODEL_AVAILABLE = True
    logger.info("✅ User model loaded successfully")
except ImportError as e:
    USER_MODEL_AVAILABLE = False
    logger.error(f"❌ User model not available: {e}")


def validate_medical_profile_data(data: dict) -> tuple:
    """
    Validate medical profile data
    
    Returns:
        (is_valid, error_message, cleaned_data)
    """
    required_fields = ['email']
    
    # Check required fields
    for field in required_fields:
        if field not in data or not data[field]:
            return False, f"Missing required field: {field}", None
    
    # Validate email format
    email = data.get('email', '')
    if '@' not in email:
        return False, "Invalid email format", None
    
    # Validate boolean fields
    boolean_fields = [
        'has_diabetes', 'has_hypertension', 'has_heart_disease',
        'has_kidney_disease', 'has_allergies', 'is_pregnant', 'is_breastfeeding'
    ]
    
    cleaned_data = {
        'email': email,
        'user_id': data.get('user_id')  # Will be set later if not provided
    }
    
    for field in boolean_fields:
        if field in data:
            value = data[field]
            if isinstance(value, bool):
                cleaned_data[field] = value
            elif isinstance(value, str):
                cleaned_data[field] = value.lower() in ['true', '1', 'yes']
            else:
                cleaned_data[field] = bool(value)
    
    # Validate allergies list
    if 'allergies' in data:
        allergies = data['allergies']
        if isinstance(allergies, list):
            cleaned_data['allergies'] = [str(a).strip() for a in allergies if a]
        elif isinstance(allergies, str):
            # Split comma-separated string
            cleaned_data['allergies'] = [a.strip() for a in allergies.split(',') if a.strip()]
        else:
            return False, "Allergies must be a list or comma-separated string", None
    
    # Validate current_medications list
    if 'current_medications' in data:
        medications = data['current_medications']
        if isinstance(medications, list):
            cleaned_data['current_medications'] = [str(m).strip() for m in medications if m]
        elif isinstance(medications, str):
            cleaned_data['current_medications'] = [m.strip() for m in medications.split(',') if m.strip()]
        else:
            return False, "Medications must be a list or comma-separated string", None
    
    # Add consent fields
    if 'consent_given' in data:
        cleaned_data['consent_given'] = bool(data['consent_given'])
    if 'consent_date' in data:
        cleaned_data['consent_date'] = data['consent_date']
    
    return True, None, cleaned_data


@csrf_exempt
@jwt_required
@patient_or_admin
def create_or_update_medical_profile(request):
    """
    Create or update user's medical profile
    
    🔐 PROTECTED: Requires JWT token
    👤 PERMISSION: Patient (own profile) or Admin (any profile)
    
    POST /api/medical/profile/
    Headers: Authorization: Bearer <access_token>
    
    Request body (JSON):
    {
        "email": "user@example.com",
        "has_diabetes": true,
        "has_hypertension": false,
        "has_heart_disease": false,
        "has_kidney_disease": false,
        "has_allergies": true,
        "allergies": ["peanuts", "shellfish"],
        "is_pregnant": false,
        "is_breastfeeding": false,
        "current_medications": ["metformin", "aspirin"],
        "consent_given": true
    }
    
    Returns:
        JSON response with profile data and status
    """
    # Debug logging
    logger.info(f"🔍 DEBUG: MEDICAL_DB_AVAILABLE = {MEDICAL_DB_AVAILABLE}")
    logger.info(f"🔍 DEBUG: USER_MODEL_AVAILABLE = {USER_MODEL_AVAILABLE}")
    logger.info(f"🔐 Authenticated user: {request.jwt_user.email} (role: {request.jwt_user.role})")
    
    if not MEDICAL_DB_AVAILABLE or not USER_MODEL_AVAILABLE:
        return JsonResponse({
            'success': False,
            'error': 'Medical profile functionality not available',
            'debug': {
                'medical_db_available': MEDICAL_DB_AVAILABLE,
                'user_model_available': USER_MODEL_AVAILABLE
            }
        }, status=503)
    
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'Method not allowed. Use POST.'
        }, status=405)
    
    try:
        # Parse request data
        if request.content_type == 'application/json':
            data = json.loads(request.body) if request.body else {}
        else:
            data = dict(request.POST)
            # Handle list values from form data
            for key in data:
                if isinstance(data[key], list) and len(data[key]) == 1:
                    data[key] = data[key][0]
        
        # Validate data
        is_valid, error_message, cleaned_data = validate_medical_profile_data(data)
        if not is_valid:
            return JsonResponse({
                'success': False,
                'error': error_message
            }, status=400)
        
        email = cleaned_data['email']
        
        # Get or create user
        user = get_or_create_user_by_email({'email': email})
        if not user:
            return JsonResponse({
                'success': False,
                'error': 'Failed to create/retrieve user'
            }, status=500)
        
        user_id = str(user.id)
        cleaned_data['user_id'] = user_id
        
        # Check if profile exists
        existing_profile = db_get_profile(user_id)
        
        if existing_profile:
            # Update existing profile
            profile = db_update_profile(user_id, cleaned_data)
            action = 'updated'
        else:
            # Create new profile - pass user_id as first argument
            profile = db_create_profile(user_id, cleaned_data)
            action = 'created'
        
        if profile:
            logger.info(f"Medical profile {action} for user: {email} by {request.jwt_user.email}")
            
            # Build response
            response_data = {
                'success': True,
                'action': action,
                'message': f'Medical profile {action} successfully',
                'profile': {
                    'user_id': user_id,
                    'email': email,
                    'has_diabetes': profile.get('has_diabetes', False),
                    'has_hypertension': profile.get('has_hypertension', False),
                    'has_heart_disease': profile.get('has_heart_disease', False),
                    'has_kidney_disease': profile.get('has_kidney_disease', False),
                    'has_allergies': profile.get('has_allergies', False),
                    'allergies': profile.get('allergies', []),
                    'is_pregnant': profile.get('is_pregnant', False),
                    'is_breastfeeding': profile.get('is_breastfeeding', False),
                    'current_medications': profile.get('current_medications', []),
                    'consent_given': profile.get('consent_given', False),
                    'last_updated': profile.get('updated_at', datetime.utcnow().isoformat())
                }
            }
            
            return JsonResponse(response_data)
        else:
            return JsonResponse({
                'success': False,
                'error': f'Failed to {action} medical profile'
            }, status=500)
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON format'
        }, status=400)
    except Exception as e:
        logger.error(f"Error creating/updating medical profile: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@jwt_required
@patient_or_admin
def get_medical_profile(request):
    """
    Get user's medical profile
    
    🔐 PROTECTED: Requires JWT token
    👤 PERMISSION: Patient (own profile) or Admin (any profile)
    
    GET /api/medical/profile/get/?email=user@example.com
    Headers: Authorization: Bearer <access_token>
    
    Returns:
        JSON response with profile data
    """
    logger.info(f"🔐 Authenticated user: {request.jwt_user.email} (role: {request.jwt_user.role})")
    
    if not MEDICAL_DB_AVAILABLE or not USER_MODEL_AVAILABLE:
        return JsonResponse({
            'success': False,
            'error': 'Medical profile functionality not available'
        }, status=503)
    
    if request.method != 'GET':
        return JsonResponse({
            'success': False,
            'error': 'Method not allowed. Use GET.'
        }, status=405)
    
    try:
        # Get email or user_id from query params
        email = request.GET.get('email')
        user_id = request.GET.get('user_id')
        
        if not email and not user_id:
            return JsonResponse({
                'success': False,
                'error': 'Either email or user_id parameter required'
            }, status=400)
        
        # Get user_id from email if needed
        if email and not user_id:
            try:
                user = User.get(User.email == email)
                user_id = str(user.id)
            except:
                return JsonResponse({
                    'success': False,
                    'error': 'User not found',
                    'profile_exists': False
                }, status=404)
        
        # Get medical profile
        profile = db_get_profile(user_id)
        
        if not profile:
            return JsonResponse({
                'success': True,
                'profile_exists': False,
                'message': 'No medical profile found for this user'
            })
        
        # Build response
        response_data = {
            'success': True,
            'profile_exists': True,
            'profile': {
                'user_id': user_id,
                'email': email or profile.get('email'),
                'has_diabetes': profile.get('has_diabetes', False),
                'has_hypertension': profile.get('has_hypertension', False),
                'has_heart_disease': profile.get('has_heart_disease', False),
                'has_kidney_disease': profile.get('has_kidney_disease', False),
                'has_allergies': profile.get('has_allergies', False),
                'allergies': profile.get('allergies', []),
                'is_pregnant': profile.get('is_pregnant', False),
                'is_breastfeeding': profile.get('is_breastfeeding', False),
                'current_medications': profile.get('current_medications', []),
                'consent_given': profile.get('consent_given', False),
                'created_at': profile.get('created_at', ''),
                'last_updated': profile.get('updated_at', '')
            }
        }
        
        return JsonResponse(response_data)
    
    except Exception as e:
        logger.error(f"Error retrieving medical profile: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@jwt_required
@patient_or_admin
def delete_medical_profile_endpoint(request):
    """
    Delete user's medical profile
    
    🔐 PROTECTED: Requires JWT token
    👤 PERMISSION: Patient (own profile) or Admin (any profile)
    
    DELETE /api/medical/profile/delete/?email=user@example.com
    Headers: Authorization: Bearer <access_token>
    
    Returns:
        JSON response with deletion status
    """
    logger.info(f"🔐 Authenticated user: {request.jwt_user.email} (role: {request.jwt_user.role})")
    
    if not MEDICAL_DB_AVAILABLE or not USER_MODEL_AVAILABLE:
        return JsonResponse({
            'success': False,
            'error': 'Medical profile functionality not available'
        }, status=503)
    
    if request.method != 'DELETE':
        return JsonResponse({
            'success': False,
            'error': 'Method not allowed. Use DELETE.'
        }, status=405)
    
    try:
        # Get email or user_id from query params
        email = request.GET.get('email')
        user_id = request.GET.get('user_id')
        
        if not email and not user_id:
            return JsonResponse({
                'success': False,
                'error': 'Either email or user_id parameter required'
            }, status=400)
        
        # Get user_id from email if needed
        if email and not user_id:
            try:
                user = User.get(User.email == email)
                user_id = str(user.id)
            except:
                return JsonResponse({
                    'success': False,
                    'error': 'User not found'
                }, status=404)
        
        # Delete medical profile
        deleted = db_delete_profile(user_id)
        
        if deleted:
            logger.info(f"Medical profile deleted for user_id: {user_id} by {request.jwt_user.email}")
            return JsonResponse({
                'success': True,
                'message': 'Medical profile deleted successfully'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Failed to delete medical profile or profile not found'
            }, status=404)
    
    except Exception as e:
        logger.error(f"Error deleting medical profile: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@jwt_required
@patient_or_admin
def get_profile_history(request):
    """
    Get medical profile update history (audit log)
    
    🔐 PROTECTED: Requires JWT token
    👤 PERMISSION: Patient (own profile) or Admin (any profile)
    
    GET /api/medical/history/?email=user@example.com&limit=10
    Headers: Authorization: Bearer <access_token>
    
    Returns:
        JSON response with audit log entries
    """
    logger.info(f"🔐 Authenticated user: {request.jwt_user.email} (role: {request.jwt_user.role})")
    
    if not MEDICAL_DB_AVAILABLE or not USER_MODEL_AVAILABLE:
        return JsonResponse({
            'success': False,
            'error': 'Medical profile functionality not available'
        }, status=503)
    
    if request.method != 'GET':
        return JsonResponse({
            'success': False,
            'error': 'Method not allowed. Use GET.'
        }, status=405)
    
    try:
        # Get parameters
        email = request.GET.get('email')
        user_id = request.GET.get('user_id')
        limit = int(request.GET.get('limit', 10))
        
        if not email and not user_id:
            return JsonResponse({
                'success': False,
                'error': 'Either email or user_id parameter required'
            }, status=400)
        
        # Get user_id from email if needed
        if email and not user_id:
            try:
                user = User.get(User.email == email)
                user_id = str(user.id)
            except:
                return JsonResponse({
                    'success': False,
                    'error': 'User not found'
                }, status=404)
        
        # Get history
        history = db_get_history(user_id, limit=limit)
        
        if not history:
            return JsonResponse({
                'success': True,
                'history': [],
                'message': 'No history found for this user'
            })
        
        # Format history entries
        formatted_history = []
        for entry in history:
            formatted_history.append({
                'timestamp': entry.get('timestamp', ''),
                'action': entry.get('action', ''),
                'changes': entry.get('changes', {}),
                'user_id': entry.get('user_id', '')
            })
        
        return JsonResponse({
            'success': True,
            'history': formatted_history,
            'total_entries': len(formatted_history)
        })
    
    except Exception as e:
        logger.error(f"Error retrieving profile history: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@jwt_required
@patient_or_admin
def update_consent(request):
    """
    Update user consent for medical profile usage
    
    🔐 PROTECTED: Requires JWT token
    👤 PERMISSION: Patient (own profile) or Admin (any profile)
    
    POST /api/medical/consent/
    Headers: Authorization: Bearer <access_token>
    
    Request body:
    {
        "email": "user@example.com",
        "consent_given": true
    }
    """
    logger.info(f"🔐 Authenticated user: {request.jwt_user.email} (role: {request.jwt_user.role})")
    
    if not MEDICAL_DB_AVAILABLE or not USER_MODEL_AVAILABLE:
        return JsonResponse({
            'success': False,
            'error': 'Medical profile functionality not available'
        }, status=503)
    
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'Method not allowed. Use POST.'
        }, status=405)
    
    try:
        # Parse request
        data = json.loads(request.body) if request.body else {}
        
        email = data.get('email')
        consent_given = data.get('consent_given')
        
        if not email:
            return JsonResponse({
                'success': False,
                'error': 'Email required'
            }, status=400)
        
        if consent_given is None:
            return JsonResponse({
                'success': False,
                'error': 'consent_given field required (true/false)'
            }, status=400)
        
        # Get user
        try:
            user = User.get(User.email == email)
            user_id = str(user.id)
        except:
            return JsonResponse({
                'success': False,
                'error': 'User not found'
            }, status=404)
        
        # Update consent
        consent_data = {
            'consent_given': bool(consent_given),
            'consent_date': datetime.utcnow().isoformat()
        }
        
        profile = db_update_profile(user_id, consent_data)
        
        if profile:
            logger.info(f"Consent {('granted' if consent_given else 'revoked')} for {email} by {request.jwt_user.email}")
            return JsonResponse({
                'success': True,
                'message': f"Consent {'granted' if consent_given else 'revoked'} successfully",
                'consent_given': bool(consent_given),
                'consent_date': consent_data['consent_date']
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Failed to update consent'
            }, status=500)
    
    except Exception as e:
        logger.error(f"Error updating consent: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)