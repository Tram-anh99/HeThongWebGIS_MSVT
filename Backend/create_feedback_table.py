"""
Create feedback table
Run this script to add the feedback table to the database
"""
import sys
sys.path.append('.')

from database import engine, Base
from models import Feedback  # Import to register the model

def create_feedback_table():
    """Create feedback table"""
    print("Creating feedback table...")
    
    try:
        # Create only the feedback table
        Feedback.__table__.create(engine, checkfirst=True)
        print("✅ Feedback table created successfully!")
    except Exception as e:
        print(f"❌ Error creating feedback table: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_feedback_table()
