import sys
import os

# Add Backend to python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from database import SessionLocal
from models.user import User
from models.farm import VungTrong

def assign_farms():
    db = SessionLocal()
    try:
        # Get farmers
        farmer1 = db.query(User).filter(User.username == "farmer1").first()
        farmer2 = db.query(User).filter(User.username == "farmer2").first()
        farmer_test = db.query(User).filter(User.username == "farmer_test_1").first()
        
        if not all([farmer1, farmer2, farmer_test]):
            print("ERROR: Not all farmer accounts found!")
            print(f"  farmer1: {farmer1}")
            print(f"  farmer2: {farmer2}")
            print(f"  farmer_test_1: {farmer_test}")
            return
        
        # Get all farms
        farms = db.query(VungTrong).limit(10).all()
        
        if len(farms) < 3:
            print(f"ERROR: Not enough farms ({len(farms)} found)")
            return
        
        # Assign farms (distribute evenly)
        assignments = [
            (farms[0], farmer1),  # Already assigned
            (farms[1], farmer2),
            (farms[2], farmer2),
            (farms[3], farmer_test),
        ]
        
        for farm, farmer in assignments:
            farm.chu_so_huu_id = farmer.id
            print(f"✓ Assigned '{farm.ten_vung}' (ID: {farm.id}) to {farmer.username} (ID: {farmer.id})")
        
        db.commit()
        print("\n✅ Successfully assigned farms to all farmers!")
        
        # Print summary
        print("\n📊 Assignment Summary:")
        for farmer in [farmer1, farmer2, farmer_test]:
            count = db.query(VungTrong).filter_by(chu_so_huu_id=farmer.id).count()
            print(f"  {farmer.username}: {count} farms")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    assign_farms()
