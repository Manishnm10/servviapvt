"""
Filter FarmStack remedy content based on medical profiles
Ensures user safety by removing contraindicated ingredients
"""
import re
import logging
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

# Import medical operations
try:
    from medical.medical_db_operations import get_medical_profile_by_user_id
    MEDICAL_DB_AVAILABLE = True
except ImportError:
    MEDICAL_DB_AVAILABLE = False
    logger.warning("⚠️ Medical DB operations not available")


class RemedyFilter:
    """
    Filters remedy content based on user's medical profile
    """
    
    # Ingredients to avoid for different conditions
    CONTRAINDICATED_INGREDIENTS = {
        'diabetes': [
            'sugar', 'honey', 'jaggery', 'maple syrup', 'sweet',
            'dates', 'raisins', 'figs', 'glucose', 'candy', 'brown sugar'
        ],
        'hypertension': [
            'salt', 'sodium', 'pickle', 'soy sauce', 'processed meat',
            'cheese', 'bacon', 'sausage', 'canned food', 'salted', 'brine'
        ],
        'kidney_disease': [
            'salt', 'banana', 'orange', 'tomato', 'potato',
            'dairy', 'nuts', 'seeds', 'whole grains', 'avocado'
        ],
        'pregnancy': [
            'papaya', 'pineapple', 'raw eggs', 'unpasteurized',
            'alcohol', 'caffeine', 'raw meat', 'liver', 'raw fish'
        ],
        'heart_disease': [
            'salt', 'butter', 'ghee', 'coconut oil', 'fried',
            'fatty meat', 'full-fat dairy', 'trans fat'
        ]
    }
    
    def filter_content_by_medical_profile(
        self,
        content_chunks: List[str],
        user_id: str
    ) -> Tuple[List[str], List[str]]:
        """
        Filter content based on user's medical profile
        
        Args:
            content_chunks: List of content strings from FarmStack
            user_id: User's ID
            
        Returns:
            Tuple of (safe_content, warnings)
        """
        if not MEDICAL_DB_AVAILABLE:
            logger.info("Medical filtering unavailable - returning all content")
            return content_chunks, []
        
        # Get user's medical profile
        try:
            profile = get_medical_profile_by_user_id(user_id)
        except Exception as e:
            logger.warning(f"Could not retrieve medical profile: {e}")
            profile = None
        
        if not profile:
            # No medical profile - return all content
            logger.info("No medical profile found - returning all content")
            return content_chunks, []
        
        logger.info(f"Applying medical filter for user {user_id}")
        
        safe_content = []
        warnings = []
        
        # Build list of ingredients to avoid
        avoid_ingredients = set()
        
        # Check for allergies
        if profile.get('has_allergies') and profile.get('allergies'):
            allergies = profile['allergies']
            avoid_ingredients.update([a.lower() for a in allergies])
            warnings.append(f"Avoiding your allergies: {', '.join(allergies)}")
            logger.info(f"Filtering for allergies: {allergies}")
        
        # Check for diabetes
        if profile.get('has_diabetes'):
            avoid_ingredients.update(self.CONTRAINDICATED_INGREDIENTS['diabetes'])
            warnings.append("Avoiding high-sugar ingredients due to diabetes")
            logger.info("Filtering for diabetes")
        
        # Check for hypertension
        if profile.get('has_hypertension'):
            avoid_ingredients.update(self.CONTRAINDICATED_INGREDIENTS['hypertension'])
            warnings.append("Avoiding high-sodium ingredients due to hypertension")
            logger.info("Filtering for hypertension")
        
        # Check for kidney disease
        if profile.get('has_kidney_disease'):
            avoid_ingredients.update(self.CONTRAINDICATED_INGREDIENTS['kidney_disease'])
            warnings.append("Avoiding kidney-restricted ingredients")
            logger.info("Filtering for kidney disease")
        
        # Check for pregnancy
        if profile.get('is_pregnant'):
            avoid_ingredients.update(self.CONTRAINDICATED_INGREDIENTS['pregnancy'])
            warnings.append("Avoiding pregnancy-unsafe ingredients")
            logger.info("Filtering for pregnancy")
        
        # Check for heart disease
        if profile.get('has_heart_disease'):
            avoid_ingredients.update(self.CONTRAINDICATED_INGREDIENTS['heart_disease'])
            warnings.append("Avoiding heart-harmful ingredients")
            logger.info("Filtering for heart disease")
        
        if not avoid_ingredients:
            logger.info("No medical restrictions found - returning all content")
            return content_chunks, []
        
        # Filter content
        filtered_out_count = 0
        for chunk in content_chunks:
            chunk_lower = chunk.lower()
            
            # Check if any contraindicated ingredient is mentioned
            has_contraindication = False
            found_ingredient = None
            
            for ingredient in avoid_ingredients:
                # Use word boundary matching to avoid false positives
                pattern = r'\b' + re.escape(ingredient) + r'\b'
                if re.search(pattern, chunk_lower):
                    has_contraindication = True
                    found_ingredient = ingredient
                    break
            
            if has_contraindication:
                filtered_out_count += 1
                logger.debug(f"Filtered out content containing: {found_ingredient}")
            else:
                safe_content.append(chunk)
        
        logger.info(f"Medical filter: {filtered_out_count}/{len(content_chunks)} chunks filtered out, {len(safe_content)} chunks safe")
        
        return safe_content, warnings
    
    def generate_medical_disclaimer(self, profile: Dict) -> str:
        """
        Generate personalized medical disclaimer
        """
        if not profile:
            return ""
        
        conditions = []
        
        if profile.get('has_diabetes'):
            conditions.append("diabetes")
        if profile.get('has_hypertension'):
            conditions.append("high blood pressure")
        if profile.get('has_heart_disease'):
            conditions.append("heart condition")
        if profile.get('has_kidney_disease'):
            conditions.append("kidney disease")
        if profile.get('is_pregnant'):
            conditions.append("pregnancy")
        if profile.get('has_allergies') and profile.get('allergies'):
            allergies = ', '.join(profile.get('allergies', []))
            conditions.append(f"allergies to {allergies}")
        
        if conditions:
            disclaimer = (
                f"⚠️ Medical Note: Considering your {', '.join(conditions)}, "
                f"I've personalized these recommendations to exclude potentially harmful ingredients. "
                f"Always consult your healthcare provider before trying new remedies."
            )
            return disclaimer
        
        return ""


def filter_remedies_by_medical_profile(
    content: List[str], 
    user_id: str
) -> Tuple[List[str], List[str], str]:
    """
    Convenience function to filter remedy content based on medical profile
    
    Args:
        content: List of content chunks
        user_id: User's ID
        
    Returns:
        Tuple of (safe_content, warnings, disclaimer)
    """
    filter_obj = RemedyFilter()
    
    # Get profile for disclaimer
    profile = None
    if MEDICAL_DB_AVAILABLE:
        try:
            from medical.medical_db_operations import get_medical_profile_by_user_id
            profile = get_medical_profile_by_user_id(user_id)
        except Exception as e:
            logger.warning(f"Could not retrieve profile for disclaimer: {e}")
    
    # Filter content
    safe_content, warnings = filter_obj.filter_content_by_medical_profile(content, user_id)
    
    # Generate disclaimer
    disclaimer = filter_obj.generate_medical_disclaimer(profile) if profile else ""
    
    return safe_content, warnings, disclaimer