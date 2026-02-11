#!/usr/bin/env python3
"""
Database migration to add loai_phan_bon column to phan_bon table.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from database import SessionLocal, engine


def run_migration():
    """Add loai_phan_bon column to phan_bon table."""
    db = SessionLocal()
    
    try:
        print("Adding loai_phan_bon column to pan_bon table...")
        
        # Add column if it doesn't exist
        db.execute(text("""
            ALTER TABLE phan_bon 
            ADD COLUMN IF NOT EXISTS loai_phan_bon VARCHAR(50);
        """))
        
        db.commit()
        print("✅ Migration complete!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_migration()
