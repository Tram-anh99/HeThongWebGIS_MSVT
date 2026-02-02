"""
Run database migration to add latitude and longitude columns
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import create_engine, text
from config import settings

def run_migration():
    """Run the migration SQL script"""
    print("=" * 70)
    print("Running migration: Add latitude/longitude to vung_trong table")
    print("=" * 70)
    
    # Create engine
    engine = create_engine(settings.DATABASE_URL)
    
    # Read migration SQL
    migration_file = os.path.join(
        os.path.dirname(__file__), 
        'add_coordinates_to_vung_trong.sql'
    )
    
    with open(migration_file, 'r') as f:
        sql = f.read()
    
    # Execute migration
    try:
        with engine.begin() as conn:
            # Execute the full script
            print(f"Executing migration SQL...")
            conn.execute(text(sql))
        
        print("\n✅ Migration completed successfully!")
        print("=" * 70)
        return True
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print("=" * 70)
        return False

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
