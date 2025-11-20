"""
Create user for FarmStack integration testing
"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

from database.database_config import db_conn
from database.models import User
import uuid

def create_test_user():
    print("\n👤 Creating user for FarmStack integration\n")
    
    db_conn.connect(reuse_if_open=True)
    
    try:
        # Check if user already exists
        email = "mohammedayaan2193@gmail.com"
        existing_user = User.select().where(User.email == email).first()
        
        if existing_user:
            print("✅ User already exists!")
            print(f"   ID: {existing_user.id}")
            print(f"   Email: {existing_user.email}")
            print(f"   Name: {existing_user.first_name} {existing_user.last_name}")
            return existing_user
        
        # Create new user
        new_user = User.create(
            id=str(uuid.uuid4()),
            email=email,
            first_name="Mohammed",
            last_name="Ayaan",
            phone="+919876543210",
            is_active=True,
            is_deleted=False
        )
        
        print("✅ User created successfully!")
        print(f"   ID: {new_user.id}")
        print(f"   Email: {new_user.email}")
        print(f"   Name: {new_user.first_name} {new_user.last_name}")
        
        return new_user
        
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        db_conn.close()

if __name__ == "__main__":
    create_test_user()