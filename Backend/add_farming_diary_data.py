#!/usr/bin/env python3
"""
Add farming diary data (LichSuCanhTac) for farms that don't have records yet.
Generates realistic data with fertilizer and pesticide usage including volumes.
"""
import sys
import os
from datetime import datetime, timedelta
import random

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models.farm import VungTrong
from models.cultivation import LichSuCanhTac, VuMua
from models.category import LoaiHoatDong
from models.input import PhanBon, ThuocBVTV


def parse_volume_to_float(volume_str):
    """Parse volume string to float, handling various formats"""
    if not volume_str:
        return 0.0
    try:
        # Remove common non-numeric characters
        cleaned = volume_str.strip().replace(',', '.')
        # Extract first number found
        import re
        match = re.search(r'\d+\.?\d*', cleaned)
        if match:
            return float(match.group())
        return 0.0
    except:
        return 0.0


def check_existing_data():
    """Check which farms have/don't have farming diary records"""
    db = SessionLocal()
    try:
        # Get all farms
        all_farms = db.query(VungTrong).all()
        total_farms = len(all_farms)
        
        # Check which farms have LichSuCanhTac records
        farms_with_diary = db.query(LichSuCanhTac.vung_trong_id).distinct().all()
        farms_with_diary_ids = {f[0] for f in farms_with_diary}
        
        farms_without_diary = [f for f in all_farms if f.id not in farms_with_diary_ids]
        
        print(f"=== Current Farming Diary Status ===")
        print(f"Total farms: {total_farms}")
        print(f"Farms with diary records: {len(farms_with_diary_ids)}")
        print(f"Farms without diary records: {len(farms_without_diary)}")
        print()
        
        return farms_without_diary
    finally:
        db.close()


def get_or_create_activity_types(db):
    """Get or create common activity types"""
    activity_names = [
        "Bón phân",
        "Phun thuốc BVTV", 
        "Tưới nước",
        "Làm cỏ",
        "Kiểm tra sâu bệnh"
    ]
    
    activities = {}
    for name in activity_names:
        activity = db.query(LoaiHoatDong).filter(LoaiHoatDong.ten_hoat_dong == name).first()
        if not activity:
            activity = LoaiHoatDong(
                ten_hoat_dong=name,
                mo_ta=f"Hoạt động {name.lower()}"
            )
            db.add(activity)
            db.flush()
        activities[name] = activity.id
    
    return activities


def get_fertilizers_and_pesticides(db):
    """Get available fertilizers and pesticides"""
    fertilizers = db.query(PhanBon).all()
    pesticides = db.query(ThuocBVTV).all()
    
    # Create defaults if none exist
    if not fertilizers:
        default_fertilizers = [
            PhanBon(ten_phan_bon="NPK 16-16-8", loai="Phân hỗn hợp", mo_ta="Phân NPK cân bằng"),
            PhanBon(ten_phan_bon="Urê", loai="Phân đạm", mo_ta="Phân đạm Urê"),
            PhanBon(ten_phan_bon="Super Lân", loai="Phân lân", mo_ta="Phân lân Super")
        ]
        for f in default_fertilizers:
            db.add(f)
        db.flush()
        fertilizers = default_fertilizers
    
    if not pesticides:
        default_pesticides = [
            ThuocBVTV(ten_thuoc="Abamectin 1.8%", loai="Thuốc trừ sâu", mo_ta="Diệt sâu sinh học"),
            ThuocBVTV(ten_thuoc="Mancozeb 80%", loai="Thuốc trừ nấm", mo_ta="Thuốc phòng trừ nấm bệnh"),
            ThuocBVTV(ten_thuoc="Imidacloprid 10%", loai="Thuốc trừ sâu", mo_ta="Thuốc diệt rệp, bọ trĩ")
        ]
        for p in default_pesticides:
            db.add(p)
        db.flush()
        pesticides = default_pesticides
    
    return fertilizers, pesticides


def create_farming_diary_for_farm(db, farm, activities, fertilizers, pesticides):
    """Create farming diary records for a single farm"""
    # Get or create a season for this farm
    season = db.query(VuMua).filter(VuMua.vung_trong_id == farm.id).first()
    if not season:
        # Create a season
        start_date = datetime.now().date() - timedelta(days=random.randint(60, 120))
        end_date = start_date + timedelta(days=random.randint(90, 180))
        season = VuMua(
            ten_vu=f"Vụ {datetime.now().year}",
            vung_trong_id=farm.id,
            ngay_bat_dau=start_date,
            ngay_ket_thuc=end_date,
            trang_thai="dang_hoat_dong"
        )
        db.add(season)
        db.flush()
    
    # Create 5-12 random activities
    num_activities = random.randint(5, 12)
    records_created = 0
    
    for i in range(num_activities):
        # Random date within last 60 days
        days_ago = random.randint(1, 60)
        activity_date = datetime.now().date() - timedelta(days=days_ago)
        
        # 50% chance for fertilizer, 30% for pesticide, 20% for other activities
        rand = random.random()
        
        if rand < 0.5:
            # Fertilizer application
            fertilizer = random.choice(fertilizers)
            volume = random.choice([25, 50, 75, 100, 150, 200])  # kg
            
            record = LichSuCanhTac(
                vung_trong_id=farm.id,
                vu_mua_id=season.id,
                loai_hoat_dong_id=activities.get("Bón phân"),
                ngay_thuc_hien=activity_date,
                chi_tiet=f"Bón {fertilizer.ten_phan_bon}",
                nguoi_thuc_hien=farm.nguoi_dai_dien or "Nhân viên",
                phan_bon_id=fertilizer.id,
                lieu_luong=str(volume),
                don_vi="kg"
            )
            db.add(record)
            records_created += 1
            
        elif rand < 0.8:
            # Pesticide application
            pesticide = random.choice(pesticides)
            volume = random.choice([0.5, 1, 1.5, 2, 2.5, 3, 4, 5])  # liters
            
            record = LichSuCanhTac(
                vung_trong_id=farm.id,
                vu_mua_id=season.id,
                loai_hoat_dong_id=activities.get("Phun thuốc BVTV"),
                ngay_thuc_hien=activity_date,
                chi_tiet=f"Phun {pesticide.ten_thuoc}",
                nguoi_thuc_hien=farm.nguoi_dai_dien or "Nhân viên",
                thuoc_bvtv_id=pesticide.id,
                lieu_luong=str(volume),
                don_vi="lít"
            )
            db.add(record)
            records_created += 1
            
        else:
            # Other activities (watering, weeding, inspection)
            activity_type = random.choice(["Tưới nước", "Làm cỏ", "Kiểm tra sâu bệnh"])
            
            record = LichSuCanhTac(
                vung_trong_id=farm.id,
                vu_mua_id=season.id,
                loai_hoat_dong_id=activities.get(activity_type),
                ngay_thuc_hien=activity_date,
                chi_tiet=f"Thực hiện {activity_type.lower()}",
                nguoi_thuc_hien=farm.nguoi_dai_dien or "Nhân viên"
            )
            db.add(record)
            records_created += 1
    
    return records_created


def main():
    """Main execution function"""
    print("=== Adding Farming Diary Data ===\n")
    
    # Check current state
    farms_without_diary = check_existing_data()
    
    if not farms_without_diary:
        print("✅ All farms already have farming diary records!")
        return
    
    print(f"📝 Adding farming diary data for {len(farms_without_diary)} farms...\n")
    
    db = SessionLocal()
    try:
        # Get or create activity types
        activities = get_or_create_activity_types(db)
        
        # Get fertilizers and pesticides
        fertilizers, pesticides = get_fertilizers_and_pesticides(db)
        
        print(f"Using {len(fertilizers)} fertilizer types and {len(pesticides)} pesticide types\n")
        
        total_records = 0
        for i, farm in enumerate(farms_without_diary, 1):
            records = create_farming_diary_for_farm(db, farm, activities, fertilizers, pesticides)
            total_records += records
            
            if i % 10 == 0:
                print(f"Processed {i}/{len(farms_without_diary)} farms...")
                db.commit()
        
        db.commit()
        
        print(f"\n✅ Successfully created {total_records} farming diary records")
        print(f"   for {len(farms_without_diary)} farms")
        
        # Verify final state
        print("\n=== Final Status ===")
        check_existing_data()
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
