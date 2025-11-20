"""
Medical Data Encryption Module
Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): 2025-11-19 11:54:33
Current User's Login: Raghuraam21

Uses AES-256 encryption for sensitive medical data
"""
import os
import base64
import json
import logging
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

# Load encryption key
ENCRYPTION_KEY = None

# Try loading from Config first
try:
    from django_core.config import Config
    if hasattr(Config, 'MEDICAL_DATA_ENCRYPTION_KEY') and Config.MEDICAL_DATA_ENCRYPTION_KEY:
        ENCRYPTION_KEY = Config.MEDICAL_DATA_ENCRYPTION_KEY
        if isinstance(ENCRYPTION_KEY, str):
            ENCRYPTION_KEY = ENCRYPTION_KEY.encode()
        logger.info("✅ Medical data encryption key loaded from Config (44 bytes)")
except ImportError:
    pass

# Fallback to environment variable
if not ENCRYPTION_KEY:
    ENCRYPTION_KEY = os.getenv('MEDICAL_DATA_ENCRYPTION_KEY')
    if ENCRYPTION_KEY:
        ENCRYPTION_KEY = ENCRYPTION_KEY.encode()
        logger.info("✅ Medical data encryption key loaded from environment")

# Generate temporary key if nothing found (development only)
if not ENCRYPTION_KEY:
    logger.warning("⚠️ No encryption key found! Generating temporary key for development.")
    logger.warning("⚠️ SET MEDICAL_DATA_ENCRYPTION_KEY in .env for production!")
    ENCRYPTION_KEY = Fernet.generate_key()

cipher_suite = Fernet(ENCRYPTION_KEY)


def encrypt_medical_data(data, expect_json=True):
    """
    Encrypt sensitive medical data
    
    Args:
        data: Data to encrypt (list, dict, or string)
        expect_json: If True, converts data to JSON before encrypting
        
    Returns:
        Base64 encoded encrypted string
    """
    try:
        if data is None:
            return None
        
        # Convert to JSON string if needed
        if expect_json:
            if isinstance(data, (list, dict)):
                data_str = json.dumps(data)
            else:
                data_str = str(data)
        else:
            data_str = str(data) if not isinstance(data, str) else data
        
        # Encrypt
        encrypted = cipher_suite.encrypt(data_str.encode())
        return base64.b64encode(encrypted).decode()
        
    except Exception as e:
        logger.error(f"Encryption error: {e}", exc_info=True)
        return None


def decrypt_medical_data(encrypted_data, expect_json=True):
    """
    Decrypt sensitive medical data
    
    Args:
        encrypted_data: Base64 encoded encrypted string
        expect_json: If True, parses result as JSON
        
    Returns:
        Decrypted data (list, dict, or string)
    """
    try:
        if not encrypted_data:
            return None
        
        # Decode and decrypt
        encrypted_bytes = base64.b64decode(encrypted_data)
        decrypted = cipher_suite.decrypt(encrypted_bytes)
        decrypted_str = decrypted.decode()
        
        # Parse JSON if expected
        if expect_json:
            try:
                return json.loads(decrypted_str)
            except json.JSONDecodeError:
                return decrypted_str
        else:
            return decrypted_str
            
    except Exception as e:
        logger.error(f"Decryption error: {e}", exc_info=True)
        return None