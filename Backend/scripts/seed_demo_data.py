#!/usr/bin/env python3
"""
Demo Data Seeding Script
Populates database with sample data for VuMua, LichSuCanhTac, and BaoDong
"""
import sys
import os
from datetime import datetime, timedelta
import random

# Add Backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from database import SessionLocal, engine
from models import VungTrong, VuMua, LichSuCanhTac, BaoDong, LoaiHoatDong, PhanBon, ThuocBVTV


def seed_vu_mua(db, farms, count=20):
    """Create active growing seasons"""
    print(f"\n📅 Seeding {count} VuMua (Growing Seasons)...")
    
    season_names = [
        "Vụ Xuân 2025", "Vụ Hè Thu 2025", "Vụ Đông 2025",
        "Vụ Xuân 2026", "Vụ Hè Thu 2026"
    ]
    
    created = 0
    for i in range(count):
        farm = random.choice(farms)
        
        # Random dates within last year and next 6 months
        start_days_ago = random.randint(30, 365)
        duration_days = random.randint(90, 180)
        
        ngay_bat_dau = datetime.now().date() - timedelta(days=start_days_ago)
        ngay_ket_thuc = ngay_bat_dau + timedelta(days=duration_days)
        
        # Status: active if end date is in future
        trang_thai = "dang_hoat_dong" if ngay_ket_thuc > datetime.now().date() else "ket_thuc"
        
        vu_mua = VuMua(
            vung_trong_id=farm.id,
            ten_vu=f"{random.choice(season_names)} - {farm.ten_vung[:20]}",
            ngay_bat_dau=ngay_bat_dau,
            ngay_ket_thuc=ngay_ket_thuc,
            trang_thai=trang_thai,
            ghi_chu=f"Demo season for {farm.ma_vung}"
        )
        
        db.add(vu_mua)
        created += 1
    
    db.commit()
    print(f"✅ Created {created} VuMua records")


def seed_lich_su_canh_tac(db, vu_mua_list, hoat_dong_list, count=150):
    """Create cultivation history records"""
    print(f"\n🌾 Seeding {count} LichSuCanhTac (Cultivation History)...")
    
    # Get available fertilizers and pesticides
    phan_bon = db.query(PhanBon).limit(5).all()
    thuoc_bvtv = db.query(ThuocBVTV).limit(5).all()
    
    chi_tiet_templates = {
        1: "Gieo hạt đều, mật độ {}, độ sâu {} cm",
        2: "Bón phân {} với liều lượng {} kg/ha",
        3: "Phun thuốc {} để phòng trừ {}",
        4: "Tưới nước đủ ẩm, thời gian {}",
        5: "Thu hoạch bằng {}, năng suất ước tính {} tấn/ha"
    }
    
    created = 0
    for i in range(count):
        vu_mua = random.choice(vu_mua_list)
        hoat_dong = random.choice(hoat_dong_list)
        
        # Random date within season range
        days_offset = random.randint(0, (vu_mua.ngay_ket_thuc - vu_mua.ngay_bat_dau).days)
        ngay_thuc_hien = vu_mua.ngay_bat_dau + timedelta(days=days_offset)
        
        # Generate appropriate details based on activity type
        if hoat_dong.id == 1:  # Gieo hạt
            chi_tiet = chi_tiet_templates[1].format(
                random.choice(["thưa", "vừa phải", "dày"]),
                random.randint(2, 5)
            )
        elif hoat_dong.id == 2:  # Bón phân
            chi_tiet = chi_tiet_templates[2].format(
                random.choice(["NPK", "DAP", "Urê"]),
                random.randint(50, 200)
            )
        elif hoat_dong.id == 3:  # Phun thuốc
            chi_tiet = chi_tiet_templates[3].format(
                random.choice(["BVTV sinh học", "thuốc hóa học"]),
                random.choice(["sâu bệnh", "cỏ dại", "nấm bệnh"])
            )
        elif hoat_dong.id == 4:  # Tưới nước
            chi_tiet = chi_tiet_templates[4].format(
                random.choice(["sáng sớm", "chiều mát", "cả ngày"])
            )
        else:  # Thu hoạch
            chi_tiet = chi_tiet_templates[5].format(
                random.choice(["máy gặt", "thủ công"]),
                round(random.uniform(3.5, 8.5), 1)
            )
        
        lich_su = LichSuCanhTac(
            vung_trong_id=vu_mua.vung_trong_id,
            vu_mua_id=vu_mua.id,
            loai_hoat_dong_id=hoat_dong.id,
            ngay_thuc_hien=ngay_thuc_hien,
            chi_tiet=chi_tiet,
            nguoi_thuc_hien=random.choice(["Nguyễn Văn A", "Trần Thị B", "Lê Văn C", "Phạm Thị D"]),
            phan_bon_id=random.choice(phan_bon).id if hoat_dong.id == 2 and phan_bon else None,
            thuoc_bvtv_id=random.choice(thuoc_bvtv).id if hoat_dong.id == 3 and thuoc_bvtv else None,
            lieu_luong=f"{random.randint(50, 200)}" if hoat_dong.id in [2, 3] else None,
            don_vi="kg/ha" if hoat_dong.id in [2, 3] else None
        )
        
        db.add(lich_su)
        created += 1
    
    db.commit()
    print(f"✅ Created {created} LichSuCanhTac records")


def seed_bao_dong(db, farms, count=15):
    """Create alert records"""
    print(f"\n⚠️ Seeding {count} BaoDong (Alerts)...")
    
    alert_types = [
        ("benh_hai", "Phát hiện sâu bệnh"),
        ("thien_tai", "Cảnh báo thiên tai"),
        ("mua_kho", "Dự báo khô hạn"),
        ("suy_dinh_duong", "Thiếu dinh dưỡng"),
        ("khac", "Vấn đề khác")
    ]
    
    severity_levels = ["thap", "trung_binh", "cao", "rat_cao"]
    statuses = ["chua_giai_quyet", "dang_xu_ly", "da_giai_quyet"]
    
    created = 0
    for i in range(count):
        farm = random.choice(farms)
        loai_bao_dong, tieu_de_base = random.choice(alert_types)
        muc_do = random.choice(severity_levels)
        trang_thai = random.choice(statuses)
        
        # Create timestamp within last 30 days
        days_ago = random.randint(1, 30)
        created_at = datetime.now() - timedelta(days=days_ago)
        
        bao_dong = BaoDong(
            vung_trong_id=farm.id,
            loai_bao_dong=loai_bao_dong,
            muc_do=muc_do,
            tieu_de=f"{tieu_de_base} tại {farm.ten_vung}",
            noi_dung=f"Phát hiện vấn đề {loai_bao_dong} mức độ {muc_do} cần xử lý. "
                     f"Diện tích ảnh hưởng khoảng {random.uniform(0.5, 5):.1f} ha.",
            trang_thai=trang_thai,
            ngay_tao=created_at
        )
        
        db.add(bao_dong)
        created += 1
    
    db.commit()
    print(f"✅ Created {created} BaoDong records")


def main():
    """Main seeding function"""
    print("="*60)
    print("🌱 Starting Demo Data Seeding")
    print("="*60)
    
    db = SessionLocal()
    
    try:
        # Get existing data
        farms = db.query(VungTrong).limit(50).all()
        hoat_dong_list = db.query(LoaiHoatDong).all()
        
        if not farms:
            print("❌ No farms found! Please add VungTrong data first.")
            return
        
        if not hoat_dong_list:
            print("❌ No LoaiHoatDong found! Database schema issue.")
            return
        
        print(f"\n📊 Found {len(farms)} farms and {len(hoat_dong_list)} activity types")
        
        # Seed VuMua
        seed_vu_mua(db, farms, count=20)
        
        # Get created vu_mua
        vu_mua_list = db.query(VuMua).all()
        print(f"📋 Total VuMua in database: {len(vu_mua_list)}")
        
        # Seed LichSuCanhTac
        if vu_mua_list:
            seed_lich_su_canh_tac(db, vu_mua_list, hoat_dong_list, count=150)
        
        # Seed BaoDong
        seed_bao_dong(db, farms, count=15)
        
        print("\n" + "="*60)
        print("✅ Demo Data Seeding Complete!")
        print("="*60)
        
        # Summary
        active_seasons = db.query(VuMua).filter(VuMua.trang_thai == "dang_hoat_dong").count()
        total_history = db.query(LichSuCanhTac).count()
        total_alerts = db.query(BaoDong).count()
        unresolved_alerts = db.query(BaoDong).filter(
            BaoDong.trang_thai.in_(["chua_giai_quyet", "dang_xu_ly"])
        ).count()
        
        print(f"\n📈 Database Summary:")
        print(f"   - Active Seasons: {active_seasons}")
        print(f"   - Cultivation Records: {total_history}")
        print(f"   - Total Alerts: {total_alerts}")
        print(f"   - Unresolved Alerts: {unresolved_alerts}")
        print()
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
