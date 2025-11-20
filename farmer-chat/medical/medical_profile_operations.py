"""
Medical Profile Operations Wrapper
Simple wrapper around medical_db_operations for easier imports
"""
import logging
from typing import Dict, List, Optional

from medical.medical_db_operations import (
    get_medical_profile_by_user_id,
    create_medical_profile,
    update_medical_profile,
    delete_medical_profile,
    get_audit_logs,
    get_user_consent,
    create_or_update_consent
)

logger = logging.getLogger(__name__)


def create_or_update_medical_profile(
    user_id: str,
    has_diabetes: bool = False,
    diabetes_type: str = None,
    has_hypertension: bool = False,
    has_heart_disease: bool = False,
    has_kidney_disease: bool = False,
    has_allergies: bool = False,
    allergies: List[str] = None,
    current_medications: List[str] = None,
    is_pregnant: bool = False,
    is_breastfeeding: bool = False,
    is_vegetarian: bool = False,
    is_vegan: bool = False,
    dietary_restrictions: List[str] = None,
    additional_notes: str = None,
    accessed_by: str = None,
    ip_address: str = None
) -> Optional[Dict]:
    """
    Create or update medical profile for a user
    
    Simplified wrapper that checks if profile exists and calls 
    appropriate create or update function.
    
    Args:
        user_id: User's unique ID
        has_diabetes: Whether user has diabetes
        diabetes_type: Type of diabetes (Type1, Type2, Gestational, Pre-diabetes)
        has_hypertension: Whether user has high blood pressure
        has_heart_disease: Whether user has heart disease
        has_kidney_disease: Whether user has kidney disease
        has_allergies: Whether user has allergies
        allergies: List of allergy items
        current_medications: List of current medications
        is_pregnant: Whether user is pregnant
        is_breastfeeding: Whether user is breastfeeding
        is_vegetarian: Whether user is vegetarian
        is_vegan: Whether user is vegan
        dietary_restrictions: List of dietary restrictions
        additional_notes: Any additional medical notes
        accessed_by: Email of person creating/updating
        ip_address: IP address of request
        
    Returns:
        Medical profile dict or None
    """
    try:
        # Check if profile already exists
        existing_profile = get_medical_profile_by_user_id(user_id, decrypt=False)
        
        profile_data = {
            'has_diabetes': has_diabetes,
            'diabetes_type': diabetes_type,
            'has_hypertension': has_hypertension,
            'has_heart_disease': has_heart_disease,
            'has_kidney_disease': has_kidney_disease,
            'has_allergies': has_allergies or (allergies and len(allergies) > 0),
            'allergies': allergies or [],
            'current_medications': current_medications or [],
            'is_pregnant': is_pregnant,
            'is_breastfeeding': is_breastfeeding,
            'is_vegetarian': is_vegetarian,
            'is_vegan': is_vegan,
            'dietary_restrictions': dietary_restrictions or [],
            'additional_notes': additional_notes or ''
        }
        
        if existing_profile:
            # Update existing profile
            logger.info(f"Updating existing medical profile for user {user_id}")
            result = update_medical_profile(
                user_id=user_id,
                updates=profile_data,
                accessed_by=accessed_by,
                ip_address=ip_address
            )
        else:
            # Create new profile
            logger.info(f"Creating new medical profile for user {user_id}")
            result = create_medical_profile(
                user_id=user_id,
                profile_data=profile_data,
                accessed_by=accessed_by,
                ip_address=ip_address
            )
        
        return result
        
    except Exception as e:
        logger.error(f"Error in create_or_update_medical_profile: {e}", exc_info=True)
        return None


# Re-export other functions for convenience
__all__ = [
    'create_or_update_medical_profile',
    'get_medical_profile_by_user_id',
    'create_medical_profile',
    'update_medical_profile',
    'delete_medical_profile',
    'get_audit_logs',
    'get_user_consent',
    'create_or_update_consent'
]