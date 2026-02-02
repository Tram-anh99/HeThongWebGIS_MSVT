"""
Add updated_at column to all tables with created_at
"""
import psycopg2
from datetime import datetime

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/webgis_msvt"

def add_updated_at_columns():
    """Add updated_at column to all tables that have created_at"""
    
    tables = ['users', 'vung_trong', 'lich_su_canh_tac', 'bao_dong', 'vu_mua']
    
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    for table in tables:
        try:
            # Check if updated_at exists
            cur.execute(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='{table}' AND column_name='updated_at';
            """)
            
            if not cur.fetchone():
                # Add updated_at column
                print(f"Adding updated_at to {table}...")
                cur.execute(f"""
                    ALTER TABLE {table} 
                    ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
                """)
                conn.commit()
                print(f"✅ Added updated_at to {table}")
            else:
                print(f"⏭️  {table} already has updated_at column")
                
        except Exception as e:
            print(f"❌ Error for {table}: {e}")
            conn.rollback()
    
    cur.close()
    conn.close()
    print("\n✅ All updates completed!")

if __name__ == "__main__":
    add_updated_at_columns()
