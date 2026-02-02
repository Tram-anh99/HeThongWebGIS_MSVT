from database import engine
from sqlalchemy import text

def add_column():
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE vung_trong ADD COLUMN chu_so_huu_id INTEGER REFERENCES users(id)"))
            conn.commit()
            print("Successfully added column 'chu_so_huu_id' to 'vung_trong'")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    add_column()
