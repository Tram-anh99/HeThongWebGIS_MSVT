"""
Script to clean up user accounts
Keep only: 1 admin, 1 farmer, and 3 department users
"""
import sys
sys.path.append('.')

from sqlalchemy.orm import Session
from database import SessionLocal
from models.user import User
from models.farm import VungTrong

def cleanup_users():
    """Delete extra users, keep only essential ones"""
    db = SessionLocal()
    
    try:
        # Get all users
        all_users = db.query(User).all()
        print(f"📊 Total users in database: {len(all_users)}\n")
        
        # Define users to keep
        users_to_keep = []
        
        # 1. Keep admin user (ID=1)
        admin = db.query(User).filter(User.role == 'admin').first()
        if admin:
            users_to_keep.append(admin.id)
            print(f"✅ Keeping admin: {admin.username} (ID: {admin.id})")
        
        # 2. Keep one farmer (first one found)
        farmer = db.query(User).filter(User.role == 'farmer').first()
        if farmer:
            users_to_keep.append(farmer.id)
            print(f"✅ Keeping farmer: {farmer.username} (ID: {farmer.id})")
        
        # 3. Keep 3 department users
        dept_users = db.query(User).filter(
            User.role.in_(['plant_dept', 'pesticide_dept', 'border_control'])
        ).all()
        for dept_user in dept_users:
            users_to_keep.append(dept_user.id)
            print(f"✅ Keeping dept user: {dept_user.username} (ID: {dept_user.id}, Role: {dept_user.role})")
        
        print(f"\n📋 Total users to keep: {len(users_to_keep)}")
        
        # Find users to delete
        users_to_delete = [u for u in all_users if u.id not in users_to_keep]
        
        if not users_to_delete:
            print("\n✨ No users to delete. Database is already clean!")
            return
        
        print(f"\n🗑️  Users to delete ({len(users_to_delete)}):")
        for user in users_to_delete:
            print(f"   - {user.username} (ID: {user.id}, Role: {user.role})")
        
        # Confirm deletion
        print("\n⚠️  This will delete the above users and set their farms' ownership to NULL.")
        response = input("Continue? (yes/no): ")
        
        if response.lower() != 'yes':
            print("❌ Cancelled.")
            return
        
        # Delete users
        deleted_count = 0
        for user in users_to_delete:
            # Nullify farm ownership first
            db.query(VungTrong).filter(VungTrong.chu_so_huu_id == user.id).update(
                {VungTrong.chu_so_huu_id: None}
            )
            # Delete user
            db.delete(user)
            deleted_count += 1
            print(f"🗑️  Deleted: {user.username}")
        
        db.commit()
        
        print(f"\n🎉 Successfully deleted {deleted_count} users!")
        
        # Show final user list
        remaining_users = db.query(User).all()
        print(f"\n📋 Final user list ({len(remaining_users)} users):")
        print("="*60)
        for user in remaining_users:
            print(f"ID: {user.id:3d} | {user.username:20s} | {user.role:15s} | {user.full_name}")
        print("="*60)
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    print("User Cleanup Script")
    print("="*60)
    cleanup_users()
