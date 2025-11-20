"""
Test Medical Profile Filtering
"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

from database.database_config import db_conn
from database.models import User
from medical.medical_profile_operations import create_or_update_medical_profile
from retrieval.content_retrieval import retrieve_content_from_api

def test_medical_filtering():
    print("\n🧪 Testing Medical Profile Filtering\n")
    
    db_conn.connect(reuse_if_open=True)
    
    try:
        # Get test user
        user = User.get(User.email == "mohammedayaan2193@gmail.com")
        user_id = str(user.id)
        
        print(f"👤 User: {user.first_name} {user.last_name}")
        print(f"   ID: {user_id}\n")
        
        # Create medical profile with diabetes
        print("📝 Creating medical profile with diabetes...")
        profile = create_or_update_medical_profile(
            user_id=user_id,
            has_diabetes=True,
            has_hypertension=False,
            has_allergies=True,
            allergies=["peanuts"],
            is_pregnant=False
        )
        print(f"✅ Medical profile created\n")
        
        # Test query
        query = "What are remedies for headache?"
        print(f"🔍 Query: {query}")
        print("=" * 70)
        
        # Retrieve with filtering
        content = retrieve_content_from_api(
            query=query,
            user_email="mohammedayaan2193@gmail.com",
            apply_medical_filter=True
        )
        
        if content:
            print(f"✅ Retrieved {len(content)} filtered chunks")
            print(f"\nFirst chunk preview:")
            print(content[0][:300] if len(content[0]) > 300 else content[0])
        else:
            print("❌ No content retrieved")
        
    finally:
        db_conn.close()

if __name__ == "__main__":
    test_medical_filtering()