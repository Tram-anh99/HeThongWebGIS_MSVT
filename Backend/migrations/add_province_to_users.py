"""
Migration script to add province_code column to users table
"""
from sqlalchemy import create_engine, Column, String, text
import sys
sys.path.append('..')
from config import settings

def upgrade():
    """Add province_code column to users table"""
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        try:
            # Add column
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN province_code VARCHAR(10)
            """))
            conn.commit()
            print("✅ Added province_code column to users table")
        except Exception as e:
            if "already exists" in str(e) or "Duplicate column" in str(e):
                print("ℹ️  Column province_code already exists")
            else:
                print(f"❌ Error: {e}")
                raise

if __name__ == "__main__":
    upgrade()
