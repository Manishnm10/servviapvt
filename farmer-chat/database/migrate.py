"""
Database Migration Script for Servvia Medical Profiling
Creates all tables including medical profiling tables
"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from database.database_config import db_conn
from database.models import (
    Language, User, Conversation, Messages, MessageMediaFiles,
    Resource, UserActions, MultilingualText, FollowUpQuestion,
    RetrievedChunk, RetrievalMetrics, RerankedChunk, RerankMetrics,
    GenerationMetrics, RephraseMetrics,
    UserMedicalProfile, UserMedicalConsent, 
    IngredientSubstitution, MedicalProfileAuditLog
)

def verify_connection():
    """Test database connection"""
    print("🔌 Testing database connection...")
    try:
        db_conn.connect(reuse_if_open=True)
        print("✅ Database connection successful!")
        print(f"📍 Connected to PostgreSQL\n")
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False

def create_all_tables():
    """Create all database tables"""
    print("📋 Creating all tables...")
    
    all_tables = [
        Language, User, Conversation, Messages, MessageMediaFiles,
        Resource, UserActions, MultilingualText, FollowUpQuestion,
        RetrievedChunk, RetrievalMetrics, RerankedChunk, RerankMetrics,
        GenerationMetrics, RephraseMetrics,
        UserMedicalProfile, UserMedicalConsent,
        IngredientSubstitution, MedicalProfileAuditLog,
    ]
    
    try:
        with db_conn:
            db_conn.create_tables(all_tables, safe=True)
            
        print(f"✅ Successfully created/verified {len(all_tables)} tables!\n")
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}\n")
        import traceback
        traceback.print_exc()
        return False

def verify_tables():
    """Verify all tables exist in database"""
    print("🔍 Verifying tables in database...")
    
    try:
        cursor = db_conn.cursor()
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        
        medical_tables = [t[0] for t in tables if 'medical' in t[0]]
        regular_tables = [t[0] for t in tables if 'medical' not in t[0]]
        
        print(f"\n📊 Total tables found: {len(tables)}")
        
        if regular_tables:
            print(f"\n📄 Regular tables ({len(regular_tables)}):")
            for table in regular_tables:
                print(f"   • {table}")
        
        if medical_tables:
            print(f"\n🏥 Medical profiling tables ({len(medical_tables)}):")
            for table in medical_tables:
                print(f"   ✓ {table}")
        else:
            print("\n⚠️  No medical profiling tables found - they will be created now.")
        
        cursor.close()
        return True
        
    except Exception as e:
        print(f"❌ Error verifying tables: {e}")
        return False

def main():
    """Main migration function"""
    print("=" * 70)
    print("🏥 SERVVIA DATABASE MIGRATION TOOL")
    print("=" * 70)
    print()
    
    if not verify_connection():
        print("\n❌ Cannot proceed without database connection!")
        return False
    
    if not create_all_tables():
        print("\n❌ Migration failed!")
        return False
    
    verify_tables()
    
    print("\n" + "=" * 70)
    print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print("\n📝 Next steps:")
    print("   1. Verify tables in pgAdmin")
    print("   2. Test medical profiling APIs")
    print("   3. Start building frontend integration")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)