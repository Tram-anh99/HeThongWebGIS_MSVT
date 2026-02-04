#!/usr/bin/env python3
"""
Populate real data for dashboard KPI cards
- Cultivation seasons (Vụ mùa)
- Farmers/Users (Nông dân)
"""
import sys
import os
from datetime import datetime, timedelta
import random

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Database connection
DB_URL = "postgresql://postgres:postgres@localhost:5432/webgis_msvt"

engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)

def check_current_data():
    """Check existing data in database"""
    session = Session()
    try:
        # Check farms
        result = session.execute(text("SELECT COUNT(*) FROM vung_trong"))
        farms_count = result.scalar()
        
        # Check cultivation seasons
        result = session.execute(text("SELECT COUNT(*) FROM vu_mua"))
        seasons_count = result.scalar()
        
        # Check users (farmers)
        result = session.execute(text("SELECT COUNT(*) FROM users WHERE role = 'farmer'"))
        farmers_count = result.scalar()
        
        print("=== Current Database State ===")
        print(f"Farms: {farms_count}")
        print(f"Cultivation Seasons: {seasons_count}")
        print(f"Farmers: {farmers_count}")
        print()
        
        return farms_count, seasons_count, farmers_count
    finally:
        session.close()

def create_farmers():
    """Create farmer users linked to farms"""
    session = Session()
    try:
        # Get farms without owners
        result = session.execute(text("""
            SELECT id, ma_vung, ten_vung, nguoi_dai_dien 
            FROM vung_trong 
            WHERE chu_so_huu_id IS NULL 
            LIMIT 50
        """))
        farms = result.fetchall()
        
        if not farms:
            print("✅ All farms already have owners")
            return 0
        
        print(f"Creating {len(farms)} farmers for farms without owners...")
        
        created = 0
        for farm in farms:
            farm_id, ma_vung, ten_vung, nguoi_dai_dien = farm
            
            # Create user for farm owner
            username = f"nongdan_{ma_vung.lower().replace('-', '_')}"
            email = f"{username}@example.com"
            full_name = nguoi_dai_dien if nguoi_dai_dien else f"Nông dân {ma_vung}"
            
            # Check if user already exists
            existing = session.execute(
                text("SELECT id FROM users WHERE email = :email"),
                {"email": email}
            ).scalar()
            
            if existing:
                user_id = existing
            else:
                # Create new user
                session.execute(text("""
                    INSERT INTO users (username, email, full_name, role, password_hash)
                    VALUES (:username, :email, :full_name, 'farmer', :password)
                """), {
                    "username": username,
                    "email": email,
                    "full_name": full_name,
                    "password": "$2b$12$dummyhash"  # Dummy hash
                })
                result = session.execute(text("SELECT lastval()"))
                user_id = result.scalar()
            
            # Link farm to user
            session.execute(
                text("UPDATE vung_trong SET chu_so_huu_id = :user_id WHERE id = :farm_id"),
                {"user_id": user_id, "farm_id": farm_id}
            )
            created += 1
            
            if created % 10 == 0:
                print(f"Created {created} farmers...")
        
        session.commit()
        print(f"\n✅ Created/linked {created} farmers to farms")
        return created
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error creating farmers: {e}")
        raise
    finally:
        session.close()

def create_cultivation_seasons():
    """Create active cultivation seasons for farms"""
    session = Session()
    try:
        # Get all farms
        result = session.execute(text("""
            SELECT id, ma_vung
            FROM vung_trong 
            ORDER BY id 
            LIMIT 100
        """))
        farms = result.fetchall()
        
        print(f"Creating cultivation seasons for {len(farms)} farms...")
        
        # Season types in Vietnam
        season_types = ["Vụ Đông Xuân", "Vụ Hè Thu", "Vụ Mùa"]
        statuses = ["đang trồng", "đang phát triển", "sắp thu hoạch"]
        
        created = 0
        for farm in farms:
            farm_id, ma_vung = farm
            
            # Check if farm already has active season
            existing = session.execute(text("""
                SELECT COUNT(*) FROM vu_mua 
                WHERE vung_trong_id = :farm_id 
                AND trang_thai IN ('đang trồng', 'đang phát triển', 'sắp thu hoạch')
            """), {"farm_id": farm_id}).scalar()
            
            if existing > 0:
                continue
            
            # Random season within last 3 months
            days_ago = random.randint(30, 90)
            start_date = datetime.now() - timedelta(days=days_ago)
            end_date = start_date + timedelta(days=random.randint(90, 180))
            
            season_name = random.choice(season_types)
            status = random.choice(statuses)
            
            session.execute(text("""
                INSERT INTO vu_mua (
                    ten_vu, vung_trong_id,
                    ngay_bat_dau, ngay_ket_thuc, trang_thai
                ) VALUES (
                    :ten_vu, :farm_id,
                    :start_date, :end_date, :status
                )
            """), {
                "ten_vu": f"{season_name} {datetime.now().year}",
                "farm_id": farm_id,
                "start_date": start_date,
                "end_date": end_date,
                "status": status
            })
            created += 1
            
            if created % 20 == 0:
                print(f"Created {created} cultivation seasons...")
        
        session.commit()
        print(f"\n✅ Created {created} active cultivation seasons")
        return created
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error creating seasons: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    print("=== Populating Dashboard Data ===\n")
    
    # Check current state
    farms, seasons, farmers = check_current_data()
    
    # Create farmers if needed
    if farmers < 50:
        print("\n📊 Creating farmer users...")
        create_farmers()
    else:
        print(f"\n✅ Already have {farmers} farmers")
    
    # Create cultivation seasons if needed
    if seasons < 50:
        print("\n📊 Creating cultivation seasons...")
        create_cultivation_seasons()
    else:
        print(f"\n✅ Already have {seasons} cultivation seasons")
    
    # Check final state
    print("\n=== After Population ===")
    check_current_data()
    
    print("\n✅ DONE! Dashboard data populated successfully")
