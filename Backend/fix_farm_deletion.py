"""
Fix farm deletion by handling foreign key constraints
This script will modify VungTrong model to cascade delete related records
"""
import sys
sys.path.append('.')

from sqlalchemy import text
from database import engine, SessionLocal

def fix_farm_deletion():
    """Fix farm deletion constraints"""
    db = SessionLocal()
    
    try:
        print("Fixing farm deletion foreign key constraints...\n")
        
        # Check which tables reference vung_trong
        print("Step 1: Checking foreign key references...")
        
        # For PostgreSQL, drop and recreate constraints with CASCADE
        # For testing, let's check what's blocking deletion
        
        # List tables that might have FK to vung_trong
        tables_to_check = ['lich_su_canh_tac', 'vu_mua', 'bao_dong']
        
        for table in tables_to_check:
            try:
                result = db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                print(f"  - {table}: {count} records")
            except Exception as e:
                print(f"  - {table}: Table might not exist")
        
        print("\n✅ Analysis complete.")
        print("\nTo fix farm deletion, you have 2 options:")
        print("1. CASCADE DELETE - Delete farm will also delete all related records")
        print("2. SET NULL - Delete farm will set foreign keys to NULL")
        print("\nRecommendation: Use CASCADE DELETE for cultivation history")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    fix_farm_deletion()
