"""
Fix admin password using bcrypt directly (no passlib)
"""
import psycopg2
import bcrypt

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/webgis_msvt"

def fix_admin_password():
    """Hash password với bcrypt library trực tiếp"""
    password = "123456"
    
    # Hash với bcrypt
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    hash_str = hashed.decode('utf-8')
    
    print(f"✅ Generated bcrypt hash for password: {password}")
    print(f"Hash preview: {hash_str[:30]}...")
    
    # Update database
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    try:
       # Update admin user
        cur.execute("""
            UPDATE users 
            SET password_hash = %s 
            WHERE username = 'admin';
        """, (hash_str,))
        
        conn.commit()
        print(f"\n✅ Updated admin password successfully!")
        
        # Verify
        cur.execute("SELECT id, username, substr(password_hash, 1, 30) as hash FROM users WHERE username='admin';")
        result = cur.fetchone()
        if result:
            print(f"✅ Verified - ID={result[0]}, username={result[1]}, hash={result[2]}...")
        
    except Exception as e:
        print(f"❌ Error updating password: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    fix_admin_password()
