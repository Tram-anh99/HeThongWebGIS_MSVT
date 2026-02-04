#!/usr/bin/env python3
"""
Check farm coordinates in database and update if missing
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import random

# Database connection
DB_URL = "postgresql://postgres:postgres@localhost:5432/webgis_msvt"

engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)

def check_coordinates():
    """Check how many farms have coordinates"""
    session = Session()
    try:
        # Count total farms
        result = session.execute(text("SELECT COUNT(*) FROM vung_trong"))
        total = result.scalar()
        
        # Count farms with coordinates
        result = session.execute(text(
            "SELECT COUNT(*) FROM vung_trong WHERE latitude IS NOT NULL AND longitude IS NOT NULL"
        ))
        with_coords = result.scalar()
        
        print(f"Total farms: {total}")
        print(f"Farms with coordinates: {with_coords}")
        print(f"Farms without coordinates: {total - with_coords}")
        
        return total, with_coords
    finally:
        session.close()

def generate_vietnam_coordinates():
    """Generate random coordinates within Vietnam boundaries"""
    # Vietnam approximate boundaries
    LAT_MIN, LAT_MAX = 8.5, 23.5  # North to South
    LNG_MIN, LNG_MAX = 102.0, 110.0  # West to East
    
    # Province centers for more realistic distribution
    province_centers = {
        'Hà Nội': (21.0285, 105.8542),
        'Hồ Chí Minh': (10.8231, 106.6297),
        'Đà Nẵng': (16.0544, 108.2022),
        'Cần Thơ': (10.0452, 105.7469),
        'Hải Phòng': (20.8449, 106.6881),
        'Gia Lai': (13.8078, 108.1090),
        'Lâm Đồng': (11.9404, 108.4583),
        'Đắk Lắk': (12.7100, 108.2378),
        'Nghệ An': (19.2342, 104.9200),
        'Thanh Hóa': (19.8067, 105.7851),
    }
    
    # Randomly pick a province center and add some variation
    center_lat, center_lng = random.choice(list(province_centers.values()))
    
    # Add random offset (±0.5 degrees, about 50km)
    lat = center_lat + random.uniform(-0.5, 0.5)
    lng = center_lng + random.uniform(-0.5, 0.5)
    
    # Ensure within Vietnam boundaries
    lat = max(LAT_MIN, min(LAT_MAX, lat))
    lng = max(LNG_MIN, min(LNG_MAX, lng))
    
    return round(lat, 6), round(lng, 6)

def update_coordinates():
    """Update farms that don't have coordinates"""
    session = Session()
    try:
        # Get farms without coordinates
        result = session.execute(text(
            "SELECT id, ma_vung, tinh_name FROM vung_trong WHERE latitude IS NULL OR longitude IS NULL"
        ))
        farms = result.fetchall()
        
        print(f"\nUpdating {len(farms)} farms with coordinates...")
        
        updated = 0
        for farm in farms:
            farm_id, ma_vung, tinh_name = farm
            lat, lng = generate_vietnam_coordinates()
            
            session.execute(
                text("UPDATE vung_trong SET latitude = :lat, longitude = :lng WHERE id = :id"),
                {"lat": lat, "lng": lng, "id": farm_id}
            )
            updated += 1
            
            if updated % 50 == 0:
                print(f"Updated {updated} farms...")
        
        session.commit()
        print(f"\n✅ Successfully updated {updated} farms with coordinates")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    print("=== Farm Coordinates Check & Update ===\n")
    
    total, with_coords = check_coordinates()
    
    if with_coords < total:
        print(f"\n⚠️ Found {total - with_coords} farms without coordinates")
        update_coordinates()
        
        # Check again
        print("\n=== After Update ===")
        check_coordinates()
    else:
        print("\n✅ All farms have coordinates!")
