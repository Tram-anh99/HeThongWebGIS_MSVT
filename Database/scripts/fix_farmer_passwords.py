"""
Fix farmer password - using bcrypt directly
"""
import psycopg2
import bcrypt

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/webgis_msvt"

def fix_farmer_passwords():
    """Hash password for farmer accounts"""
    password = "123456"
    
    # Hash với bcrypt
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    hash_str = hashed.decode('utf-8')
    
    print(f"✅ Generated bcrypt hash for password: {password}")
    
    # Update database
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    try:
       # Update farmer users
        cur.execute("""
            UPDATE users 
            SET password_hash = %s 
            WHERE role = 'farmer';
        """, (hash_str,))
        
        updated_rows = cur.rowcount
        conn.commit()
        print(f"\n✅ Updated passwords for {updated_rows} farmer accounts successfully!")
        
        # Verify
        cur.execute("SELECT id, username, role FROM users WHERE role='farmer';")
        users = cur.fetchall()
        for user in users:
            print(f"✅ Verified Farmer: ID={user[0]}, username={user[1]}, role={user[2]}")
        
    except Exception as e:
        print(f"❌ Error updating passwords: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    fix_farmer_passwords()
