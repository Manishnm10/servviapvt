"""Test configuration loading"""
from django_core.config import Config

def test_config():
    print("🔍 Testing Configuration\n")
    
    print("=" * 70)
    print("DATABASE CONFIGURATION")
    print("=" * 70)
    print(f"DB Name: {Config.DB_NAME}")
    print(f"DB User: {Config.DB_USER}")
    print(f"DB Host: {Config.DB_HOST}")
    print(f"DB Port: {Config.DB_PORT}")
    
    print("\n" + "=" * 70)
    print("MEDICAL PROFILING CONFIGURATION")
    print("=" * 70)
    print(f"Enabled: {Config.ENABLE_MEDICAL_PROFILING}")
    print(f"Encryption Key Set: {'Yes' if Config.MEDICAL_DATA_ENCRYPTION_KEY else 'No'}")
    print(f"Audit Retention: {Config.MEDICAL_AUDIT_LOG_RETENTION_DAYS} days")
    print(f"Max Profile Version: {Config.MEDICAL_PROFILE_MAX_VERSION}")
    
    print("\n" + "=" * 70)
    print("VALIDATION")
    print("=" * 70)
    
    try:
        Config.validate_medical_config()
        print("✅ Medical configuration is valid")
    except Exception as e:
        print(f"❌ Medical configuration error: {e}")
    
    print(f"\n✅ Medical profiling enabled: {Config.is_medical_profiling_enabled()}")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    test_config()