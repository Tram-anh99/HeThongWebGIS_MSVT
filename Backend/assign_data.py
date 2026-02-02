import sys
import os

# Add Backend to python path if run from inside Backend
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from database import SessionLocal
from models.user import User
from models.farm import VungTrong

def assign_farm():
    db = SessionLocal()
    try:
        farmer = db.query(User).filter(User.username == "farmer_test_1").first()
        if not farmer:
            print("Farmer 'farmer_test_1' not found!")
            return

        print(f"Farmer found: {farmer.username} (ID: {farmer.id})")

        # Find any farm to assign
        farm = db.query(VungTrong).first()
        if not farm:
            print("No farms found in database!")
            return

        print(f"Farm found: {farm.ten_vung} (ID: {farm.id})")
        
        # Assign
        farm.chu_so_huu_id = farmer.id
        db.commit()
        print(f"SUCCESS: Assigned farm '{farm.ten_vung}' to user '{farmer.username}'")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    assign_farm()
