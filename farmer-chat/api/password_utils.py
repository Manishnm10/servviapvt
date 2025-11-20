"""
Password Security Utilities
Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): 2025-11-19 16:28:15
Current User's Login: Raghuraam21

Provides secure password hashing, validation, and strength checking
Uses bcrypt for password hashing (industry standard)
"""
import bcrypt
import re
from typing import Tuple, Dict
import logging

logger = logging.getLogger(__name__)


class PasswordValidator:
    """
    Password validation and strength checking
    
    Requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    """
    
    # Password requirements
    MIN_LENGTH = 8
    MAX_LENGTH = 128
    
    # Regex patterns
    UPPERCASE_PATTERN = re.compile(r'[A-Z]')
    LOWERCASE_PATTERN = re.compile(r'[a-z]')
    DIGIT_PATTERN = re.compile(r'\d')
    SPECIAL_CHAR_PATTERN = re.compile(r'[!@#$%^&*(),.?":{}|<>]')
    
    @classmethod
    def validate_password_strength(cls, password: str) -> Tuple[bool, Dict[str, any]]:
        """
        Validate password strength
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (is_valid, validation_result)
            
        Example:
            >>> is_valid, result = PasswordValidator.validate_password_strength("MyPass123!")
            >>> print(result)
            {
                'valid': True,
                'strength': 'strong',
                'score': 5,
                'requirements_met': {
                    'length': True,
                    'uppercase': True,
                    'lowercase': True,
                    'digit': True,
                    'special_char': True
                },
                'feedback': []
            }
        """
        result = {
            'valid': True,
            'strength': 'weak',
            'score': 0,
            'requirements_met': {
                'length': False,
                'uppercase': False,
                'lowercase': False,
                'digit': False,
                'special_char': False
            },
            'feedback': []
        }
        
        # Check if password is provided
        if not password:
            result['valid'] = False
            result['feedback'].append('Password is required')
            return False, result
        
        # Check length
        if len(password) < cls.MIN_LENGTH:
            result['valid'] = False
            result['feedback'].append(f'Password must be at least {cls.MIN_LENGTH} characters long')
        elif len(password) > cls.MAX_LENGTH:
            result['valid'] = False
            result['feedback'].append(f'Password must not exceed {cls.MAX_LENGTH} characters')
        else:
            result['requirements_met']['length'] = True
            result['score'] += 1
        
        # Check for uppercase letter
        if cls.UPPERCASE_PATTERN.search(password):
            result['requirements_met']['uppercase'] = True
            result['score'] += 1
        else:
            result['valid'] = False
            result['feedback'].append('Password must contain at least one uppercase letter')
        
        # Check for lowercase letter
        if cls.LOWERCASE_PATTERN.search(password):
            result['requirements_met']['lowercase'] = True
            result['score'] += 1
        else:
            result['valid'] = False
            result['feedback'].append('Password must contain at least one lowercase letter')
        
        # Check for digit
        if cls.DIGIT_PATTERN.search(password):
            result['requirements_met']['digit'] = True
            result['score'] += 1
        else:
            result['valid'] = False
            result['feedback'].append('Password must contain at least one digit')
        
        # Check for special character
        if cls.SPECIAL_CHAR_PATTERN.search(password):
            result['requirements_met']['special_char'] = True
            result['score'] += 1
        else:
            result['valid'] = False
            result['feedback'].append('Password must contain at least one special character (!@#$%^&*...)')
        
        # Determine strength
        if result['score'] >= 5:
            result['strength'] = 'strong'
        elif result['score'] >= 3:
            result['strength'] = 'medium'
        else:
            result['strength'] = 'weak'
        
        # Check for common weak patterns
        common_patterns = [
            'password', '12345678', 'qwerty', 'abc123', 
            'letmein', 'welcome', 'monkey', '123456789'
        ]
        
        if password.lower() in common_patterns:
            result['valid'] = False
            result['strength'] = 'weak'
            result['feedback'].append('Password is too common. Please choose a stronger password.')
        
        if result['valid']:
            result['feedback'] = ['Password meets all requirements']
        
        return result['valid'], result


class PasswordHasher:
    """
    Secure password hashing using bcrypt
    
    Bcrypt automatically handles:
    - Salt generation
    - Multiple rounds of hashing
    - Timing attack protection
    """
    
    # Bcrypt work factor (number of rounds)
    # Higher = more secure but slower
    # 12 rounds is a good balance (takes ~250ms)
    WORK_FACTOR = 12
    
    @classmethod
    def hash_password(cls, password: str) -> str:
        """
        Hash a password using bcrypt
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password (base64 encoded)
            
        Example:
            >>> hashed = PasswordHasher.hash_password("MySecurePass123!")
            >>> print(hashed)
            '$2b$12$...'
        """
        if not password:
            raise ValueError("Password cannot be empty")
        
        # Convert password to bytes
        password_bytes = password.encode('utf-8')
        
        # Generate salt and hash password
        salt = bcrypt.gensalt(rounds=cls.WORK_FACTOR)
        hashed = bcrypt.hashpw(password_bytes, salt)
        
        # Return as string
        return hashed.decode('utf-8')
    
    @classmethod
    def verify_password(cls, password: str, hashed_password: str) -> bool:
        """
        Verify a password against a hash
        
        Args:
            password: Plain text password to verify
            hashed_password: Hashed password from database
            
        Returns:
            True if password matches, False otherwise
            
        Example:
            >>> hashed = PasswordHasher.hash_password("MyPass123!")
            >>> PasswordHasher.verify_password("MyPass123!", hashed)
            True
            >>> PasswordHasher.verify_password("WrongPass", hashed)
            False
        """
        if not password or not hashed_password:
            return False
        
        try:
            # Convert to bytes
            password_bytes = password.encode('utf-8')
            hashed_bytes = hashed_password.encode('utf-8')
            
            # Verify password
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        
        except Exception as e:
            logger.error(f"Password verification error: {e}", exc_info=True)
            return False
    
    @classmethod
    def needs_rehash(cls, hashed_password: str) -> bool:
        """
        Check if password hash needs to be updated
        (e.g., if work factor has increased)
        
        Args:
            hashed_password: Hashed password from database
            
        Returns:
            True if password should be rehashed
        """
        try:
            hashed_bytes = hashed_password.encode('utf-8')
            current_work_factor = bcrypt.hashpw(b'test', bcrypt.gensalt(rounds=cls.WORK_FACTOR))
            
            # Extract work factor from hash
            # bcrypt format: $2b$[work_factor]$[salt+hash]
            stored_work_factor = int(hashed_password.split('$')[2])
            
            return stored_work_factor < cls.WORK_FACTOR
        
        except Exception:
            return False


def validate_email(email: str) -> Tuple[bool, str]:
    """
    Validate email format
    
    Args:
        email: Email address to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not email:
        return False, "Email is required"
    
    # Basic email regex
    email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    if not email_pattern.match(email):
        return False, "Invalid email format"
    
    if len(email) > 254:
        return False, "Email is too long"
    
    return True, ""


# Example usage and testing
if __name__ == "__main__":
    print("=" * 70)
    print("  Password Security Utilities - Test Suite")
    print("  Current Date and Time (UTC): 2025-11-19 16:28:15")
    print("  Current User: Raghuraam21")
    print("=" * 70)
    
    # Test password validation
    print("\n📋 Testing Password Validation:")
    print("-" * 70)
    
    test_passwords = [
        ("weak", "Test password: 'weak'"),
        ("MyPass123!", "Test password: 'MyPass123!' (strong)"),
        ("short", "Test password: 'short' (too short)"),
        ("nouppercase123!", "Test password: 'nouppercase123!' (no uppercase)"),
        ("NOLOWERCASE123!", "Test password: 'NOLOWERCASE123!' (no lowercase)"),
        ("NoDigits!@#", "Test password: 'NoDigits!@#' (no digits)"),
        ("NoSpecial123", "Test password: 'NoSpecial123' (no special char)"),
    ]
    
    for password, description in test_passwords:
        is_valid, result = PasswordValidator.validate_password_strength(password)
        print(f"\n{description}")
        print(f"   Valid: {is_valid}")
        print(f"   Strength: {result['strength']}")
        print(f"   Score: {result['score']}/5")
        print(f"   Feedback: {', '.join(result['feedback'])}")
    
    # Test password hashing
    print("\n" + "=" * 70)
    print("📋 Testing Password Hashing:")
    print("-" * 70)
    
    test_password = "MySecurePass123!"
    print(f"\nOriginal password: {test_password}")
    
    # Hash password
    hashed = PasswordHasher.hash_password(test_password)
    print(f"Hashed password: {hashed}")
    print(f"Hash length: {len(hashed)} characters")
    
    # Verify correct password
    is_correct = PasswordHasher.verify_password(test_password, hashed)
    print(f"\nVerify correct password: {is_correct} ✅")
    
    # Verify wrong password
    is_wrong = PasswordHasher.verify_password("WrongPassword123!", hashed)
    print(f"Verify wrong password: {is_wrong} ❌")
    
    # Test email validation
    print("\n" + "=" * 70)
    print("📋 Testing Email Validation:")
    print("-" * 70)
    
    test_emails = [
        "user@example.com",
        "invalid-email",
        "user@",
        "@example.com",
        "user@@example.com",
        "a" * 250 + "@example.com",
    ]
    
    for email in test_emails:
        is_valid, error = validate_email(email)
        status = "✅ Valid" if is_valid else f"❌ Invalid: {error}"
        print(f"\n{email}")
        print(f"   {status}")
    
    print("\n" + "=" * 70)
    print("✅ All tests completed!")
    print("=" * 70 + "\n")