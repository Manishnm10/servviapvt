"""
Medical Profile API Router
FastAPI endpoints for medical profiling operations
"""
from fastapi import APIRouter, HTTPException, Request, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
import logging

from medical.medical_db_operations import (
    create_medical_profile,
    get_medical_profile_by_user_id,
    update_medical_profile,
    delete_medical_profile,
    get_audit_logs,
    get_ingredient_substitutes,
    create_ingredient_substitution,
    get_user_consent,
    create_or_update_consent
)
from database.models import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/medical", tags=["Medical Profiling"])


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class MedicalProfileCreate(BaseModel):
    """Schema for creating medical profile"""
    has_diabetes: bool = False
    diabetes_type: Optional[str] = Field(None, regex="^(type1|type2|gestational)$")
    has_hypertension: bool = False
    has_heart_disease: bool = False
    has_kidney_disease: bool = False
    is_pregnant: bool = False
    is_breastfeeding: bool = False
    has_allergies: bool = False
    allergies: List[str] = Field(default_factory=list)
    current_medications: List[str] = Field(default_factory=list)
    is_vegetarian: bool = False
    is_vegan: bool = False
    dietary_restrictions: List[str] = Field(default_factory=list)
    additional_notes: str = ""
    
    @validator('diabetes_type')
    def validate_diabetes_type(cls, v, values):
        if values.get('has_diabetes') and not v:
            raise ValueError('diabetes_type is required when has_diabetes is True')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "has_diabetes": True,
                "diabetes_type": "type2",
                "has_hypertension": False,
                "allergies": ["peanuts", "shellfish"],
                "current_medications": ["metformin"],
                "dietary_restrictions": ["low-carb", "no-sugar"],
                "additional_notes": "Monitor blood sugar regularly"
            }
        }


class MedicalProfileUpdate(BaseModel):
    """Schema for updating medical profile"""
    has_diabetes: Optional[bool] = None
    diabetes_type: Optional[str] = Field(None, regex="^(type1|type2|gestational)$")
    has_hypertension: Optional[bool] = None
    has_heart_disease: Optional[bool] = None
    has_kidney_disease: Optional[bool] = None
    is_pregnant: Optional[bool] = None
    is_breastfeeding: Optional[bool] = None
    has_allergies: Optional[bool] = None
    allergies: Optional[List[str]] = None
    current_medications: Optional[List[str]] = None
    is_vegetarian: Optional[bool] = None
    is_vegan: Optional[bool] = None
    dietary_restrictions: Optional[List[str]] = None
    additional_notes: Optional[str] = None


class ConsentCreate(BaseModel):
    """Schema for consent management"""
    consent_given: bool
    consent_version: str = "1.0"
    
    class Config:
        schema_extra = {
            "example": {
                "consent_given": True,
                "consent_version": "1.0"
            }
        }


class IngredientSubstitutionCreate(BaseModel):
    """Schema for creating ingredient substitution"""
    original_ingredient: str
    substitute_ingredient: str
    reason: str
    condition_type: str
    confidence_level: float = Field(0.8, ge=0.0, le=1.0)
    category: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "original_ingredient": "sugar",
                "substitute_ingredient": "stevia",
                "reason": "Diabetes-friendly sweetener",
                "condition_type": "diabetes",
                "confidence_level": 0.9,
                "category": "sweetener"
            }
        }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_client_ip(request: Request) -> str:
    """Extract client IP address from request"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0]
    return request.client.host


def get_current_user_email(request: Request) -> str:
    """
    Extract current user email from request
    TODO: Replace with actual authentication
    """
    # For now, return from header or default
    return request.headers.get("X-User-Email", "anonymous@servvia.com")


# ============================================================================
# MEDICAL PROFILE ENDPOINTS
# ============================================================================

@router.post("/profile/{user_id}", status_code=status.HTTP_201_CREATED)
async def create_profile(
    user_id: str,
    profile_data: MedicalProfileCreate,
    request: Request
):
    """
    Create a new medical profile for user
    
    - **user_id**: User's unique identifier
    - **profile_data**: Medical profile information
    
    Returns the created medical profile with encrypted sensitive data
    """
    try:
        # Verify user exists
        try:
            user = User.get_by_id(user_id)
        except:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} not found"
            )
        
        # Check if profile already exists
        existing = get_medical_profile_by_user_id(user_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Medical profile already exists for this user. Use PUT to update."
            )
        
        # Create profile
        profile = create_medical_profile(
            user_id=user_id,
            profile_data=profile_data.dict(),
            accessed_by=get_current_user_email(request),
            ip_address=get_client_ip(request)
        )
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create medical profile"
            )
        
        return {
            "status": "success",
            "message": "Medical profile created successfully",
            "data": profile
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating medical profile: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/profile/{user_id}")
async def get_profile(user_id: str, request: Request):
    """
    Retrieve user's medical profile
    
    - **user_id**: User's unique identifier
    
    Returns decrypted medical profile data
    """
    try:
        profile = get_medical_profile_by_user_id(user_id)
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No medical profile found for user {user_id}"
            )
        
        # Log access
        from medical.medical_db_operations import log_medical_audit
        log_medical_audit(
            user_id=user_id,
            action="VIEW",
            action_details={"viewed_by": get_current_user_email(request)},
            accessed_by=get_current_user_email(request),
            ip_address=get_client_ip(request)
        )
        
        return {
            "status": "success",
            "data": profile
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving medical profile: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/profile/{user_id}")
async def update_profile(
    user_id: str,
    updates: MedicalProfileUpdate,
    request: Request
):
    """
    Update existing medical profile
    
    - **user_id**: User's unique identifier
    - **updates**: Fields to update
    
    Returns updated medical profile
    """
    try:
        # Filter out None values
        update_data = {k: v for k, v in updates.dict().items() if v is not None}
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No update data provided"
            )
        
        profile = update_medical_profile(
            user_id=user_id,
            updates=update_data,
            accessed_by=get_current_user_email(request),
            ip_address=get_client_ip(request)
        )
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No medical profile found for user {user_id}"
            )
        
        return {
            "status": "success",
            "message": "Medical profile updated successfully",
            "data": profile
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating medical profile: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/profile/{user_id}")
async def delete_profile(
    user_id: str,
    request: Request,
    hard_delete: bool = False
):
    """
    Delete user's medical profile
    
    - **user_id**: User's unique identifier
    - **hard_delete**: If true, permanently delete; else soft delete
    
    Returns success message
    """
    try:
        success = delete_medical_profile(
            user_id=user_id,
            accessed_by=get_current_user_email(request),
            ip_address=get_client_ip(request),
            hard_delete=hard_delete
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No medical profile found for user {user_id}"
            )
        
        return {
            "status": "success",
            "message": f"Medical profile {'permanently deleted' if hard_delete else 'deactivated'} successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting medical profile: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ============================================================================
# AUDIT LOG ENDPOINTS
# ============================================================================

@router.get("/profile/{user_id}/audit-logs")
async def get_profile_audit_logs(
    user_id: str,
    limit: int = 50,
    request: Request
):
    """
    Retrieve audit logs for user's medical profile
    
    - **user_id**: User's unique identifier
    - **limit**: Maximum number of logs to return (default: 50)
    
    Returns list of audit log entries
    """
    try:
        logs = get_audit_logs(user_id, limit=limit)
        
        return {
            "status": "success",
            "count": len(logs),
            "data": logs
        }
        
    except Exception as e:
        logger.error(f"Error retrieving audit logs: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ============================================================================
# CONSENT ENDPOINTS
# ============================================================================

@router.get("/consent/{user_id}")
async def get_consent(user_id: str):
    """
    Get user's consent status
    
    - **user_id**: User's unique identifier
    
    Returns consent information
    """
    try:
        consent = get_user_consent(user_id)
        
        if not consent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No consent record found for user {user_id}"
            )
        
        return {
            "status": "success",
            "data": consent
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving consent: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/consent/{user_id}")
async def create_consent(
    user_id: str,
    consent_data: ConsentCreate,
    request: Request
):
    """
    Create or update user consent
    
    - **user_id**: User's unique identifier
    - **consent_data**: Consent information
    
    Returns consent record
    """
    try:
        consent = create_or_update_consent(
            user_id=user_id,
            consent_given=consent_data.consent_given,
            consent_version=consent_data.consent_version,
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("User-Agent")
        )
        
        if not consent:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create/update consent"
            )
        
        return {
            "status": "success",
            "message": "Consent recorded successfully",
            "data": consent
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating consent: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ============================================================================
# INGREDIENT SUBSTITUTION ENDPOINTS
# ============================================================================

@router.get("/substitutes/{ingredient}")
async def get_substitutes(
    ingredient: str,
    condition_type: Optional[str] = None
):
    """
    Get ingredient substitutes based on medical conditions
    
    - **ingredient**: Original ingredient name
    - **condition_type**: Optional filter by condition (diabetes, allergy_peanuts, etc.)
    
    Returns list of suitable substitutes
    """
    try:
        substitutes = get_ingredient_substitutes(ingredient, condition_type)
        
        if not substitutes:
            return {
                "status": "success",
                "message": f"No substitutes found for '{ingredient}'",
                "data": []
            }
        
        return {
            "status": "success",
            "count": len(substitutes),
            "data": substitutes
        }
        
    except Exception as e:
        logger.error(f"Error retrieving substitutes: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/substitutes", status_code=status.HTTP_201_CREATED)
async def add_substitute(substitution: IngredientSubstitutionCreate):
    """
    Add a new ingredient substitution
    
    - **substitution**: Substitution details
    
    Returns created substitution record
    """
    try:
        result = create_ingredient_substitution(
            original=substitution.original_ingredient,
            substitute=substitution.substitute_ingredient,
            reason=substitution.reason,
            condition_type=substitution.condition_type,
            confidence=substitution.confidence_level,
            category=substitution.category
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create ingredient substitution"
            )
        
        return {
            "status": "success",
            "message": "Ingredient substitution created successfully",
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating substitution: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ============================================================================
# HEALTH CHECK
# ============================================================================

@router.get("/health")
async def health_check():
    """Health check endpoint for medical profiling API"""
    from django_core.config import Config
    
    return {
        "status": "healthy",
        "service": "Medical Profiling API",
        "version": "1.0.0",
        "medical_profiling_enabled": Config.is_medical_profiling_enabled(),
        "timestamp": datetime.utcnow().isoformat()
    }