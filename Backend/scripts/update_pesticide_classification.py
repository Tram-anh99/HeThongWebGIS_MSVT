"""
Script to add loai_thuoc classification to ThuocBVTV table

This script reads the ThuocBaoVeThucVat.xlsx file and updates the database
to ensure proper classification of pesticides by type.
"""

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db, engine
from models import ThuocBVTV

def classify_pesticide_type(doi_tuong_phong_tru):
    """
    Classify pesticide based on target pest description
    """
    if not doi_tuong_phong_tru or pd.isna(doi_tuong_phong_tru):
        return "Khác"
    
    doi_tuong = str(doi_tuong_phong_tru).lower()
    
    # Thuốc trừ sâu (Insecticide)
    if any(word in doi_tuong for word in ['sâu', 'rệp', 'bọ', 'nhện', 'kiến', 'muỗi']):
        return "Thuốc trừ sâu"
    
    # Thuốc diệt cỏ (Herbicide)
    if any(word in doi_tuong for word in ['cỏ', 'cỏ dại']):
        return "Thuốc diệt cỏ"
    
    # Thuốc trừ nấm (Fungicide)
    if any(word in doi_tuong for word in ['nấm', 'bệnh', 'virus', 'vi khuẩn']):
        return "Thuốc trừ nấm"
    
    # Thuốc điều hòa sinh trưởng
    if any(word in doi_tuong for word in ['sinh trưởng', 'tăng trưởng', 'kích thích']):
        return "Thuốc điều hòa sinh trưởng"
    
    return "Khác"

def update_thuoc_bvtv_classification():
    """
    Update loai_thuoc field in thuoc_bvtv table
    """
    print("=== Updating ThuocBVTV Classification ===\n")
    
    # Create database session
    db = next(get_db())
    
    try:
        # Fetch all records
        records = db.query(ThuocBVTV).all()
        print(f"Found {len(records)} pesticide records")
        
        classification_stats = {}
        updated_count = 0
        
        for record in records:
            # Classify based on doi_tuong_phong_tru
            loai_thuoc = classify_pesticide_type(record.doi_tuong_phong_tru)
            
            # Update if different
            if record.loai_thuoc != loai_thuoc:
                record.loai_thuoc = loai_thuoc
                updated_count += 1
            
            # Track statistics
            classification_stats[loai_thuoc] = classification_stats.get(loai_thuoc, 0) + 1
        
        # Commit changes
        db.commit()
        
        print(f"\n✓ Updated {updated_count} records")
        print(f"\n=== Classification Statistics ===")
        for loai, count in sorted(classification_stats.items()):
            print(f"{loai}: {count} records")
        
    except Exception as e:
        db.rollback()
        print(f"✗ Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    update_thuoc_bvtv_classification()
    print("\n=== Done ===")
