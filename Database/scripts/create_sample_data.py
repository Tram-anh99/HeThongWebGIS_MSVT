"""
========== Create Sample Data ==========
Tạo dữ liệu mẫu cho hệ thống WebGIS MSVT
Author: HeThongWebGIS_MSVT
"""

import sys
import os
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../Backend'))
sys.path.insert(0, backend_path)

from database import SessionLocal
from models import *
from datetime import datetime, date, timedelta
import random
import hashlib

# Simple password hashing (for demo purposes)
def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_sample_users(db):
    """Tạo sample users"""
    print("\n📝 Creating sample users...")
    
    users_data = [
        {"username": "admin", "email": "admin@webgis.com", "full_name": "Qu\u1ea3n trị viên", "role": "admin"},
        {"username": "farmer1", "email": "farmer1@example.com", "full_name": "Nguyễn Văn A", "role": "farmer"},
        {"username": "farmer2", "email": "farmer2@example.com", "full_name": "Trần Thị B", "role": "farmer"},
        {"username": "viewer1", "email": "viewer1@example.com", "full_name": "Lê Văn C", "role": "viewer"},
    ]
    
    users = []
    for user_data in users_data:
        user = User(
            username=user_data["username"],
            email=user_data["email"],
            full_name=user_data["full_name"],
            password_hash=hash_password("123456"),  # Default password
            role=user_data["role"],
            is_active=True
        )
        db.add(user)
        users.append(user)
    
    db.commit()
    print(f"✅ Created {len(users)} users")
    return users


def create_sample_categories(db):
    """Tạo danh mục mẫu"""
    print("\n📝 Creating sample categories...")
    
    # Loại cây trồng
    cay_trong = [
        {"ten_cay": "Lúa", "ten_khoa_hoc": "Oryza sativa"},
        {"ten_cay": "Cà phê", "ten_khoa_hoc": "Coffea"},
        {"ten_cay": "Cao su", "ten_khoa_hoc": "Hevea brasiliensis"},
        {"ten_cay": "Hồ tiêu", "ten_khoa_hoc": "Piper nigrum"},
        {"ten_cay": "Rau màu", "ten_khoa_hoc": "Vegetables"},
    ]
    
    for item in cay_trong:
        db.add(LoaiCayTrong(**item))
    
    # Loại hoạt động
    hoat_dong = [
        {"ten_hoat_dong": "Gieo hạt/Trồng", "mo_ta": "Gieo hạt hoặc trồng cây con"},
        {"ten_hoat_dong": "Bón phân", "mo_ta": "Bón phân dinh dưỡng"},
        {"ten_hoat_dong": "Phun thuốc BVTV", "mo_ta": "Phun thuốc bảo vệ thực vật"},
        {"ten_hoat_dong": "Tưới nước", "mo_ta": "Tưới tiêu cho cây trồng"},
        {"ten_hoat_dong": "Thu hoạch", "mo_ta": "Thu hoạch sản phẩm"},
        {"ten_hoat_dong": "Làm cỏ", "mo_ta": "Làm cỏ, dọn vệ sinh vườn"},
    ]
    
    for item in hoat_dong:
        db.add(LoaiHoatDong(**item))
    
    # Phân bón
    phan_bon = [
        {"ten_phan_bon": "Phân NPK 16-16-8", "nha_san_xuat": "Phú Mỹ", "lieu_luong_khuyen_nghi": "300-500 kg/ha"},
        {"ten_phan_bon": "Phân Urê", "nha_san_xuat": "Hà Bắc", "lieu_luong_khuyen_nghi": "200-300 kg/ha"},
        {"ten_phan_bon": "Phân DAP", "nha_san_xuat": "Lâm Thao", "lieu_luong_khuyen_nghi": "100-200 kg/ha"},
    ]
    
    for item in phan_bon:
        db.add(PhanBon(**item))
    
    # Thuốc BVTV
    thuoc = [
        {"ten_thuoc": "Actara 25WG", "hoat_chat": "Thiamethoxam", "nha_san_xuat": "Syngenta"},
        {"ten_thuoc": "Bassa 50EC", "hoat_chat": "Quinalphos", "nha_san_xuat": "Syngenta"},
        {"ten_thuoc": "Score 250EC", "hoat_chat": "Difenoconazole", "nha_san_xuat": "Syngenta"},
    ]
    
    for item in thuoc:
        db.add(ThuocBVTV(**item))
    
    db.commit()
    print("✅ Created sample categories")


def create_sample_farms(db):
    """Tạo sample vùng trồng"""
    print("\n📝 Creating sample farms...")
    
    # Lấy tỉnh để gán vùng trồng
    tinhs = db.query(Tinh).limit(10).all()
    users = db.query(User).filter(User.role == "farmer").all()
    loai_cay = db.query(LoaiCayTrong).all()
    
    if not tinhs:
        print("⚠️  No provinces found, skipping farms")
        return []
    
    farms_data = [
        {"ten_vung": "Vườn lúa Đồng Bằng", "dien_tich": 5.2, "x": 105.8, "y": 21.0},
        {"ten_vung": "Vườn cà phê Tây Nguyên", "dien_tich": 3.7, "x": 108.0, "y": 12.7},
        {"ten_vung": "Vườn cao su miền Đông", "dien_tich": 12.5, "x": 106.7, "y": 11.5},
        {"ten_vung": "Vườn hồ tiêu Đông Nam Bộ", "dien_tich": 2.8, "x": 107.1, "y": 11.9},
        {"ten_vung": "Vườn rau sạch Đà Lạt", "dien_tich": 1.5, "x": 108.4, "y": 11.9},
    ]
    
    farms = []
    for i, farm_data in enumerate(farms_data):
        farm = VungTrong(
            ma_vung=f"MSVT{2024000 + i + 1:06d}",
            ten_vung=farm_data["ten_vung"],
            dien_tich=farm_data["dien_tich"],
            tinh_id=tinhs[i % len(tinhs)].id if tinhs else None,
            chu_so_huu_id=users[i % len(users)].id if users else None,
            loai_cay_id=loai_cay[i % len(loai_cay)].id if loai_cay else None,
            x=farm_data["x"],
            y=farm_data["y"],
            trang_thai="Đang hoạt động"
        )
        db.add(farm)
        farms.append(farm)
    
    db.commit()
    print(f"✅ Created {len(farms)} sample farms")
    return farms


def create_sample_seasons(db, farms):
    """Tạo sample vụ mùa"""
    print("\n📝 Creating sample seasons...")
    
    seasons = []
    for i, farm in enumerate(farms[:3]):  # Tạo vụ mùa cho 3 vùng đầu
        season = VuMua(
            ten_vu=f"Vụ {['Xuân', 'Hè', 'Thu'][i % 3]} 2024",
            vung_trong_id=farm.id,
            ngay_bat_dau=date(2024, (i*3 + 1) % 12 + 1, 1),
            ngay_ket_thuc=None if i == 0 else date(2024, (i*3 + 4) % 12 + 1, 1),
            trang_thai="Đang diễn ra" if i == 0 else "Đã kết thúc"
        )
        db.add(season)
        seasons.append(season)
    
    db.commit()
    print(f"✅ Created {len(seasons)} sample seasons")
    return seasons


def create_sample_history(db, farms, seasons):
    """Tạo sample lịch sử canh tác"""
    print("\n📝 Creating sample cultivation history...")
    
    hoat_dong = db.query(LoaiHoatDong).all()
    phan_bon = db.query(PhanBon).all()
    thuoc = db.query(ThuocBVTV).all()
    
    if not hoat_dong:
        print("⚠️  No activity types found, skipping history")
        return []
    
    history_records = []
    
    for i, farm in enumerate(farms[:3]):
        season = seasons[i] if i < len(seasons) else None
        
        # Tạo 5-10 records lịch sử cho mỗi vùng
        num_records = random.randint(5, 10)
        base_date = date.today() - timedelta(days=90)
        
        for j in range(num_records):
            record = LichSuCanhTac(
                vung_trong_id=farm.id,
                vu_mua_id=season.id if season else None,
                loai_hoat_dong_id=hoat_dong[j % len(hoat_dong)].id,
                ngay_thuc_hien=base_date + timedelta(days=j*7),
                chi_tiet=f"Hoạt động {j+1} tại {farm.ten_vung}",
                nguoi_thuc_hien="Nông dân chủ vườn",
                phan_bon_id=phan_bon[j % len(phan_bon)].id if phan_bon and j % 3 == 0 else None,
                thuoc_bvtv_id=thuoc[j % len(thuoc)].id if thuoc and j % 4 == 1 else None,
                lieu_luong=f"{random.randint(100, 500)} kg/ha" if j % 2 == 0 else None,
                don_vi="kg/ha"
            )
            db.add(record)
            history_records.append(record)
    
    db.commit()
    print(f"✅ Created {len(history_records)} historical records")
    return history_records


def main():
    """Main function"""
    print("=" * 70)
    print("Creating Sample Data for WebGIS MSVT")
    print("=" * 70)
    
    db = SessionLocal()
    
    try:
        # 1. Create users
        users = create_sample_users(db)
        
        # 2. Create categories
        create_sample_categories(db)
        
        # 3. Create farms
        farms = create_sample_farms(db)
        
        # 4. Create seasons
        seasons = create_sample_seasons(db, farms)
        
        # 5. Create cultivation history
        history = create_sample_history(db, farms, seasons)
        
        print("\n" + "=" * 70)
        print("✅ Sample data creation completed!")
        print("=" * 70)
        print(f"\n📊 Summary:")
        print(f"   - Users: {len(users)}")
        print(f"   - Farms: {len(farms)}")
        print(f"   - Seasons: {len(seasons)}")
        print(f"   - History records: {len(history)}")
        
        print("\n🔐 Login credentials:")
        print("   - admin / 123456 (Admin)")
        print("   - farmer1 / 123456 (Farmer)")
        print("   - farmer2 / 123456 (Farmer)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
