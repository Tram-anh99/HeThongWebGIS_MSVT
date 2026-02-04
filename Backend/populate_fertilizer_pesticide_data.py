"""
Script to populate fertilizer and pesticide demo data for all farms
Generates realistic data based on farm area and randomization
"""
import random
from sqlalchemy.orm import Session
from database import SessionLocal
from models.farm import VungTrong

def populate_fertilizer_pesticide_data():
    """Populate fertilizer and pesticide volumes with realistic demo data"""
    db: Session = SessionLocal()
    
    try:
        # Get all farms
        farms = db.query(VungTrong).all()
        print(f"Found {len(farms)} farms to update...")
        
        updated_count = 0
        for farm in farms:
            # Get farm area (default to 1 if not available)
            area = float(farm.dien_tich) if farm.dien_tich else 1.0
            
            # Calculate fertilizer volume based on area
            # Typical usage: 200-500 kg per hectare
            # Add randomization ±30% for variety
            base_fertilizer = area * random.uniform(200, 500)
            fertilizer_variation = random.uniform(0.7, 1.3)
            farm.fertilizer_volume = round(base_fertilizer * fertilizer_variation, 2)
            
            # Calculate pesticide volume based on area
            # Typical usage: 5-20 kg per hectare
            # Add randomization ±40% for variety
            base_pesticide = area * random.uniform(5, 20)
            pesticide_variation = random.uniform(0.6, 1.4)
            farm.pesticide_volume = round(base_pesticide * pesticide_variation, 2)
            
            updated_count += 1
            
            if updated_count % 20 == 0:
                print(f"  Updated {updated_count} farms...")
        
        # Commit all changes
        db.commit()
        print(f"\n✅ Successfully updated {updated_count} farms with fertilizer and pesticide data!")
        
        # Show some statistics
        total_fertilizer = db.query(VungTrong).count()
        avg_fertilizer = db.query(VungTrong).filter(VungTrong.fertilizer_volume > 0).count()
        avg_pesticide = db.query(VungTrong).filter(VungTrong.pesticide_volume > 0).count()
        
        print(f"\nStatistics:")
        print(f"  Total farms: {total_fertilizer}")
        print(f"  Farms with fertilizer data: {avg_fertilizer}")
        print(f"  Farms with pesticide data: {avg_pesticide}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("🌾 Populating fertilizer and pesticide demo data...\n")
    populate_fertilizer_pesticide_data()
