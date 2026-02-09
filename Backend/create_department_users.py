"""
Script to create 3 new department users
Chi cục Trồng trọt, Chi cục Thuốc BVTV, Cơ quan Cửa khẩu
"""
import sys
sys.path.append('.')

from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models.user import User
from utils.auth import get_password_hash

def create_department_users():
    """Create 3 new department user accounts"""
    db = SessionLocal()
    
    try:
        # Check if users already exist
        existing_users = db.query(User).filter(
            User.username.in_(['chiucuctrongtrot', 'chiucucthuocbvtv', 'coquancuakhau'])
        ).all()
        
        if existing_users:
            print(f"⚠️  Found {len(existing_users)} existing department users:")
            for u in existing_users:
                print(f"   - {u.username} ({u.role})")
            print("\nSkipping creation to avoid duplicates.")
            return
        
        # Define new users
        new_users = [
            {
                'username': 'chiucuctrongtrot',
                'email': 'trongtrot@mard.gov.vn',
                'full_name': 'Chi cục Trồng trọt',
                'role': 'plant_dept',
                'password': 'TrongTrot2024'
            },
            {
                'username': 'chiucucthuocbvtv',
                'email': 'bvtv@mard.gov.vn',
                'full_name': 'Chi cục Thuốc BVTV',
                'role': 'pesticide_dept',
                'password': 'BVTV2024'
            },
            {
                'username': 'coquancuakhau',
                'email': 'cuakhau@customs.gov.vn',
                'full_name': 'Cơ quan Cửa khẩu',
                'role': 'border_control',
                'password': 'CuaKhau2024'
            }
        ]
        
        # Create users
        created_count = 0
        for user_data in new_users:
            password = user_data.pop('password')
            user = User(
                **user_data,
                password_hash=get_password_hash(password),
                is_active=True
            )
            db.add(user)
            created_count += 1
            print(f"✅ Created: {user_data['username']} ({user_data['role']})")
        
        db.commit()
        print(f"\n🎉 Successfully created {created_count} department users!")
        
        # Print login credentials
        print("\n" + "="*60)
        print("LOGIN CREDENTIALS:")
        print("="*60)
        for user_data in new_users:
            # Re-extract password (it was popped earlier)
            if user_data['username'] == 'chiucuctrongtrot':
                pwd = 'TrongTrot2024'
            elif user_data['username'] == 'chiucucthuocbvtv':
                pwd = 'BVTV2024'
            else:
                pwd = 'CuaKhau2024'
            
            print(f"\nUsername: {user_data['username']}")
            print(f"Password: {pwd}")
            print(f"Role: {user_data['role']}")
        print("="*60)
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Creating 3 department users...\n")
    create_department_users()
