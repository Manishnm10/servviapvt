"""
Medical Database Operations
Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): 2025-11-19 11:28:45
Current User's Login: Raghuraam21

Handles CRUD operations for medical profiling with encryption and audit logging
"""
import logging
import json
import datetime
from typing import List, Dict, Optional
from database.database_config import db_conn
from database.models import (
    UserMedicalProfile, 
    UserMedicalConsent, 
    IngredientSubstitution,
    MedicalProfileAuditLog,
    User
)
from peewee import DoesNotExist
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from security.medical_encryption import encrypt_medical_data, decrypt_medical_data

logger = logging.getLogger(__name__)


def get_medical_profile_by_user_id(user_id, decrypt=True):
    """
    Retrieve user's medical profile
    
    Args:
        user_id: User ID
        decrypt: Whether to decrypt sensitive fields
        
    Returns:
        dict with medical profile data or None
    """
    try:
        # Don't use 'with db_conn' - just query directly
        profile = UserMedicalProfile.get(UserMedicalProfile.user == user_id)
        
        profile_data = {
            "id": profile.id,
            "user_id": user_id,
            "has_diabetes": profile.has_diabetes,
            "diabetes_type": profile.diabetes_type,
            "has_hypertension": profile.has_hypertension,
            "has_heart_disease": profile.has_heart_disease,
            "has_kidney_disease": profile.has_kidney_disease,
            "is_pregnant": profile.is_pregnant,
            "is_breastfeeding": profile.is_breastfeeding,
            "has_allergies": profile.has_allergies,
            "is_vegetarian": profile.is_vegetarian,
            "is_vegan": profile.is_vegan,
            "dietary_restrictions": json.loads(profile.dietary_restrictions) if profile.dietary_restrictions else [],
            "last_updated": profile.last_updated.isoformat() if profile.last_updated else None,
            "created_at": profile.created_on.isoformat() if hasattr(profile, 'created_on') and profile.created_on else None,
            "updated_at": profile.last_updated.isoformat() if profile.last_updated else None,
            "profile_version": profile.profile_version,
        }
        
        if decrypt:
            try:
                profile_data["allergies"] = decrypt_medical_data(profile.allergies_encrypted) or []
                profile_data["current_medications"] = decrypt_medical_data(profile.current_medications_encrypted) or []
                profile_data["additional_notes"] = decrypt_medical_data(profile.additional_notes_encrypted, expect_json=False) or ""
            except Exception as e:
                logger.error(f"Error decrypting medical data: {e}")
                profile_data["allergies"] = []
                profile_data["current_medications"] = []
                profile_data["additional_notes"] = ""
        
        return profile_data
        
    except DoesNotExist:
        logger.info(f"No medical profile found for user {user_id}")
        return None
    except Exception as e:
        logger.error(f"Error retrieving medical profile: {e}", exc_info=True)
        return None


def create_medical_profile(user_id, profile_data, accessed_by=None, ip_address=None):
    """
    Create a new medical profile for user
    
    Args:
        user_id: User ID
        profile_data: dict with medical information
        accessed_by: email of person creating (for audit)
        ip_address: IP address of request
        
    Returns:
        Created profile dict or None
    """
    try:
        # Use atomic transaction for all operations
        with db_conn.atomic():
            # Encrypt sensitive fields
            allergies_enc = encrypt_medical_data(profile_data.get("allergies", []))
            medications_enc = encrypt_medical_data(profile_data.get("current_medications", []))
            notes_enc = encrypt_medical_data(profile_data.get("additional_notes", ""))
            
            # Create profile
            profile = UserMedicalProfile.create(
                user=user_id,
                has_diabetes=profile_data.get("has_diabetes", False),
                diabetes_type=profile_data.get("diabetes_type"),
                has_hypertension=profile_data.get("has_hypertension", False),
                has_heart_disease=profile_data.get("has_heart_disease", False),
                has_kidney_disease=profile_data.get("has_kidney_disease", False),
                is_pregnant=profile_data.get("is_pregnant", False),
                is_breastfeeding=profile_data.get("is_breastfeeding", False),
                has_allergies=profile_data.get("has_allergies", False) or len(profile_data.get("allergies", [])) > 0,
                allergies_encrypted=allergies_enc,
                current_medications_encrypted=medications_enc,
                is_vegetarian=profile_data.get("is_vegetarian", False),
                is_vegan=profile_data.get("is_vegan", False),
                dietary_restrictions=json.dumps(profile_data.get("dietary_restrictions", [])),
                additional_notes_encrypted=notes_enc,
                last_updated=datetime.datetime.now(),
                profile_version=1
            )
            
            # Audit log - create within the same transaction
            MedicalProfileAuditLog.create(
                user=user_id,
                action="CREATE",
                action_details=json.dumps({
                    "fields_created": list(profile_data.keys()),
                    "has_diabetes": profile_data.get("has_diabetes", False),
                    "has_allergies": profile_data.get("has_allergies", False),
                }),
                accessed_by=accessed_by or "system",
                ip_address=ip_address or "127.0.0.1",
            )
            
            logger.info(f"✅ Medical profile created for user {user_id}")
        
        # Retrieve and return the created profile (outside transaction)
        return get_medical_profile_by_user_id(user_id)
        
    except Exception as e:
        logger.error(f"Error creating medical profile: {e}", exc_info=True)
        return None


def update_medical_profile(user_id, updates, accessed_by=None, ip_address=None):
    """
    Update existing medical profile
    
    Args:
        user_id: User ID
        updates: dict with fields to update
        accessed_by: email of person updating
        ip_address: IP address of request
        
    Returns:
        Updated profile dict or None
    """
    try:
        with db_conn.atomic():
            profile = UserMedicalProfile.get(UserMedicalProfile.user == user_id)
            
            updated_fields = []
            
            # Handle encrypted fields
            if "allergies" in updates:
                profile.allergies_encrypted = encrypt_medical_data(updates["allergies"])
                profile.has_allergies = len(updates["allergies"]) > 0
                updated_fields.append("allergies")
                
            if "current_medications" in updates:
                profile.current_medications_encrypted = encrypt_medical_data(updates["current_medications"])
                updated_fields.append("current_medications")
                
            if "additional_notes" in updates:
                profile.additional_notes_encrypted = encrypt_medical_data(updates["additional_notes"])
                updated_fields.append("additional_notes")
            
            # Handle regular fields
            regular_fields = [
                "has_diabetes", "diabetes_type", "has_hypertension", 
                "has_heart_disease", "has_kidney_disease", "is_pregnant", 
                "is_breastfeeding", "is_vegetarian", "is_vegan"
            ]
            
            for field in regular_fields:
                if field in updates:
                    setattr(profile, field, updates[field])
                    updated_fields.append(field)
            
            if "dietary_restrictions" in updates:
                profile.dietary_restrictions = json.dumps(updates["dietary_restrictions"])
                updated_fields.append("dietary_restrictions")
            
            profile.last_updated = datetime.datetime.now()
            profile.profile_version += 1
            profile.save()
            
            # Audit log - create within the same transaction
            MedicalProfileAuditLog.create(
                user=user_id,
                action="UPDATE",
                action_details=json.dumps({
                    "updated_fields": updated_fields,
                    "profile_version": profile.profile_version
                }),
                accessed_by=accessed_by or "system",
                ip_address=ip_address or "127.0.0.1",
            )
            
            logger.info(f"✅ Medical profile updated for user {user_id} (version {profile.profile_version})")
        
        # Retrieve and return updated profile (outside transaction)
        return get_medical_profile_by_user_id(user_id)
        
    except DoesNotExist:
        logger.warning(f"No medical profile found for user {user_id} to update")
        return None
    except Exception as e:
        logger.error(f"Error updating medical profile: {e}", exc_info=True)
        return None


def delete_medical_profile(user_id, accessed_by=None, ip_address=None, hard_delete=False):
    """
    Delete (soft or hard) a medical profile
    
    Args:
        user_id: User ID
        accessed_by: email of person deleting
        ip_address: IP address of request
        hard_delete: If True, permanently delete; if False, soft delete
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with db_conn.atomic():
            profile = UserMedicalProfile.get(UserMedicalProfile.user == user_id)
            
            if hard_delete:
                profile.delete_instance()
                action = "HARD_DELETE"
            else:
                profile.is_deleted = True
                profile.is_active = False
                profile.save()
                action = "SOFT_DELETE"
            
            # Audit log
            MedicalProfileAuditLog.create(
                user=user_id,
                action=action,
                action_details=json.dumps({"deletion_type": "hard" if hard_delete else "soft"}),
                accessed_by=accessed_by or "system",
                ip_address=ip_address or "127.0.0.1",
            )
            
            logger.info(f"✅ Medical profile {'permanently deleted' if hard_delete else 'soft deleted'} for user {user_id}")
            return True
            
    except DoesNotExist:
        logger.warning(f"No medical profile found for user {user_id} to delete")
        return False
    except Exception as e:
        logger.error(f"Error deleting medical profile: {e}", exc_info=True)
        return False


def get_medical_profile_history(user_id: str, limit: int = 10) -> List[Dict]:
    """
    Get medical profile update history (audit log) for a user
    
    Args:
        user_id: User's UUID
        limit: Maximum number of history entries to return
        
    Returns:
        List of audit log entries with timestamps and changes
    """
    try:
        # Query audit log entries for this user
        audit_entries = (
            MedicalProfileAuditLog
            .select()
            .where(MedicalProfileAuditLog.user == user_id)
            .order_by(MedicalProfileAuditLog.created_on.desc())
            .limit(limit)
        )
        
        if not audit_entries:
            logger.info(f"No audit history found for user_id: {user_id}")
            return []
        
        # Format audit entries
        history = []
        for entry in audit_entries:
            history.append({
                'timestamp': entry.created_on.isoformat() if entry.created_on else '',
                'action': entry.action or 'unknown',
                'changes': json.loads(entry.action_details) if entry.action_details else {},
                'user_id': str(entry.user.id) if hasattr(entry, 'user') else str(user_id),
                'accessed_by': entry.accessed_by or 'unknown',
                'ip_address': entry.ip_address or 'unknown'
            })
        
        logger.info(f"Retrieved {len(history)} audit entries for user_id: {user_id}")
        return history
        
    except Exception as e:
        logger.error(f"Error retrieving medical profile history: {e}", exc_info=True)
        return []


def log_medical_audit(user_id, action, action_details=None, accessed_by=None, ip_address=None):
    """
    Log medical profile access/modification
    
    NOTE: This should only be called WITHIN an existing atomic transaction,
    or it will create its own transaction which can cause issues.
    
    Args:
        user_id: User ID
        action: Action type (VIEW, CREATE, UPDATE, DELETE, etc.)
        action_details: dict with additional details
        accessed_by: email of person performing action
        ip_address: IP address of request
    """
    try:
        # Don't use 'with db_conn' - assumes we're already in a transaction
        MedicalProfileAuditLog.create(
            user=user_id,
            action=action.upper(),
            action_details=json.dumps(action_details) if action_details else None,
            accessed_by=accessed_by or "system",
            ip_address=ip_address or "127.0.0.1",
        )
    except Exception as e:
        logger.error(f"Failed to create audit log: {e}", exc_info=True)


def get_audit_logs(user_id, limit=50):
    """
    Retrieve audit logs for a user's medical profile
    
    Args:
        user_id: User ID
        limit: Maximum number of logs to return
        
    Returns:
        list of audit log dicts
    """
    try:
        logs = (
            MedicalProfileAuditLog
            .select()
            .where(MedicalProfileAuditLog.user == user_id)
            .order_by(MedicalProfileAuditLog.created_on.desc())
            .limit(limit)
        )
        
        results = []
        for log in logs:
            results.append({
                "id": log.id,
                "action": log.action,
                "action_details": json.loads(log.action_details) if log.action_details else None,
                "accessed_by": log.accessed_by,
                "ip_address": log.ip_address,
                "timestamp": log.created_on.isoformat() if log.created_on else None,
            })
        
        return results
        
    except Exception as e:
        logger.error(f"Error retrieving audit logs: {e}", exc_info=True)
        return []


def get_ingredient_substitutes(ingredient, condition_type=None):
    """
    Get safe substitutes for an ingredient based on medical condition
    
    Args:
        ingredient: Original ingredient (e.g., "sugar", "turmeric")
        condition_type: Medical condition (e.g., "diabetes", "allergy_turmeric")
                       If None, returns all substitutes for that ingredient
        
    Returns:
        list of substitute dicts or None
    """
    try:
        query = (
            IngredientSubstitution
            .select()
            .where(
                (IngredientSubstitution.original_ingredient.contains(ingredient.lower())) |
                (IngredientSubstitution.original_ingredient == ingredient.lower())
            )
        )
        
        if condition_type:
            query = query.where(IngredientSubstitution.condition_type == condition_type.lower())
        
        substitutes = query
        
        results = []
        for sub in substitutes:
            results.append({
                "id": sub.id,
                "original": sub.original_ingredient,
                "substitute": sub.substitute_ingredient,
                "reason": sub.reason,
                "condition_type": sub.condition_type,
                "confidence": sub.confidence_level,
                "category": sub.category if hasattr(sub, 'category') else None,
            })
        
        return results if results else None
        
    except Exception as e:
        logger.error(f"Error fetching substitutes for {ingredient}: {e}", exc_info=True)
        return None


def create_ingredient_substitution(original, substitute, reason, condition_type, confidence=0.8, category=None):
    """
    Create a new ingredient substitution entry
    
    Args:
        original: Original ingredient name
        substitute: Substitute ingredient name
        reason: Reason for substitution
        condition_type: Medical condition (e.g., "diabetes", "allergy_peanuts")
        confidence: Confidence level (0.0 to 1.0)
        category: Optional category (e.g., "sweetener", "grain")
        
    Returns:
        Created substitution dict or None
    """
    try:
        with db_conn.atomic():
            sub = IngredientSubstitution.create(
                original_ingredient=original.lower(),
                substitute_ingredient=substitute.lower(),
                reason=reason,
                condition_type=condition_type.lower(),
                confidence_level=confidence,
                category=category
            )
            
            logger.info(f"✅ Ingredient substitution created: {original} → {substitute}")
            
            return {
                "id": sub.id,
                "original": sub.original_ingredient,
                "substitute": sub.substitute_ingredient,
                "reason": sub.reason,
                "condition_type": sub.condition_type,
                "confidence": sub.confidence_level,
                "category": sub.category if hasattr(sub, 'category') else None,
            }
            
    except Exception as e:
        logger.error(f"Error creating ingredient substitution: {e}", exc_info=True)
        return None


def get_user_consent(user_id):
    """
    Get user's medical data consent status
    
    Args:
        user_id: User ID
        
    Returns:
        dict with consent data or None
    """
    try:
        consent = UserMedicalConsent.get(UserMedicalConsent.user == user_id)
        
        return {
            "id": consent.id,
            "user_id": user_id,
            "consent_given": consent.consent_given,
            "consent_date": consent.consent_date.isoformat() if consent.consent_date else None,
            "consent_version": consent.consent_version,
            "ip_address": consent.ip_address,
        }
        
    except DoesNotExist:
        logger.info(f"No consent record found for user {user_id}")
        return None
    except Exception as e:
        logger.error(f"Error retrieving consent: {e}", exc_info=True)
        return None


def create_or_update_consent(user_id, consent_given, consent_version="1.0", ip_address=None, user_agent=None):
    """
    Create or update user consent
    
    Args:
        user_id: User ID
        consent_given: Boolean consent status
        consent_version: Version of consent form
        ip_address: IP address of request
        user_agent: User agent string
        
    Returns:
        Consent dict or None
    """
    try:
        with db_conn.atomic():
            try:
                # Try to get existing consent
                consent = UserMedicalConsent.get(UserMedicalConsent.user == user_id)
                consent.consent_given = consent_given
                consent.consent_date = datetime.datetime.now()
                consent.consent_version = consent_version
                consent.ip_address = ip_address or "127.0.0.1"
                consent.user_agent = user_agent
                consent.save()
                action = "updated"
            except DoesNotExist:
                # Create new consent
                consent = UserMedicalConsent.create(
                    user=user_id,
                    consent_given=consent_given,
                    consent_date=datetime.datetime.now(),
                    consent_version=consent_version,
                    ip_address=ip_address or "127.0.0.1",
                    user_agent=user_agent
                )
                action = "created"
            
            # Audit log
            MedicalProfileAuditLog.create(
                user=user_id,
                action=f"CONSENT_{action.upper()}",
                action_details=json.dumps({
                    "consent_given": consent_given,
                    "consent_version": consent_version
                }),
                accessed_by="user",
                ip_address=ip_address or "127.0.0.1",
            )
            
            logger.info(f"✅ Consent {action} for user {user_id}: {consent_given}")
        
        return get_user_consent(user_id)
        
    except Exception as e:
        logger.error(f"Error creating/updating consent: {e}", exc_info=True)
        return None