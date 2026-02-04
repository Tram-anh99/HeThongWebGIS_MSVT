from database import engine
from sqlalchemy import text

def add_fertilizer_pesticide_columns():
    """Add fertilizer_volume and pesticide_volume columns to vung_trong table"""
    with engine.connect() as conn:
        try:
            # Add fertilizer_volume column
            conn.execute(text(
                "ALTER TABLE vung_trong ADD COLUMN fertilizer_volume NUMERIC(10, 2) DEFAULT 0"
            ))
            print("✓ Added column 'fertilizer_volume' to 'vung_trong'")
        except Exception as e:
            print(f"fertilizer_volume: {e}")
        
        try:
            # Add pesticide_volume column
            conn.execute(text(
                "ALTER TABLE vung_trong ADD COLUMN pesticide_volume NUMERIC(10, 2) DEFAULT 0"
            ))
            print("✓ Added column 'pesticide_volume' to 'vung_trong'")
        except Exception as e:
            print(f"pesticide_volume: {e}")
        
        conn.commit()
        print("\n✅ Migration completed!")

if __name__ == "__main__":
    add_fertilizer_pesticide_columns()
