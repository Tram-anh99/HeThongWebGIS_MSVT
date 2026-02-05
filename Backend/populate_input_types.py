"""
Populate database with sample crop types, fertilizers, and pesticides,
then assign them randomly to existing farms.
"""
import os
import sys
import random
from sqlalchemy import create_engine, func, text
from sqlalchemy.orm import sessionmaker

# Add parent directory to path
sys.path.append(os.path.dirname(__file__))

from models.category import LoaiCayTrong
from models.input import PhanBon, ThuocBVTV
from models.farm import VungTrong

# Database connection
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/webgis_msvt')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Sample data
CROP_TYPES = [
    {"ten_cay": "Thanh long", "ten_khoa_hoc": "Hylocereus undatus"},
    {"ten_cay": "Chuối", "ten_khoa_hoc": "Musa"},
    {"ten_cay": "Dừa", "ten_khoa_hoc": "Cocos nucifera"},
    {"ten_cay": "Xoài", "ten_khoa_hoc": "Mangifera indica"},
    {"ten_cay": "Nhãn", "ten_khoa_hoc": "Dimocarpus longan"},
    {"ten_cay": "Vải", "ten_khoa_hoc": "Litchi chinensis"},
    {"ten_cay": "Cam", "ten_khoa_hoc": "Citrus sinensis"},
    {"ten_cay": "Bưởi", "ten_khoa_hoc": "Citrus maxima"},
]

FERTILIZER_TYPES = [
    {"ten_phan_bon": "NPK 16-16-8", "nha_san_xuat": "Công ty Phân bón Miền Nam", "thanh_phan": "Nitơ 16%, Lân 16%, Kali 8%"},
    {"ten_phan_bon": "Urê 46%", "nha_san_xuat": "Nhà máy Đạm Phú Mỹ", "thanh_phan": "Nitơ 46%"},
    {"ten_phan_bon": "Phân hữu cơ vi sinh", "nha_san_xuat": "Công ty TNHH Phân bón Hữu cơ Việt", "thanh_phan": "Chất hữu cơ 45%, vi sinh vật"},
    {"ten_phan_bon": "Lân Supe", "nha_san_xuat": "Công ty Cổ phần Hóa chất Đức Giang", "thanh_phan": "P2O5 16%"},
    {"ten_phan_bon": "DAP", "nha_san_xuat": "Công ty Phân bón Hóa học", "thanh_phan": "Nitơ 18%, P2O5 46%"},
]

PESTICIDE_TYPES = [
    {"ten_thuoc": "Abamectin 1.8% EC", "loai_thuoc": "Thuốc trừ sâu", "hoat_chat": "Abamectin", "doi_tuong_phong_tru": "Bọ trĩ, nhện đỏ"},
    {"ten_thuoc": "Imidacloprid 70% WP", "loai_thuoc": "Thuốc trừ sâu", "hoat_chat": "Imidacloprid", "doi_tuong_phong_tru": "Rầy, bọ phấn, bọ trĩ"},
    {"ten_thuoc": "Glyphosate 480g/l SL", "loai_thuoc": "Thuốc diệt cỏ", "hoat_chat": "Glyphosate", "doi_tuong_phong_tru": "Cỏ dại"},
    {"ten_thuoc": "Mancozeb 80% WP", "loai_thuoc": "Thuốc trừ nấm", "hoat_chat": "Mancozeb", "doi_tuong_phong_tru": "Bệnh đốm lá, phấn trắng"},
    {"ten_thuoc": "Cypermethrin 10% EC", "loai_thuoc": "Thuốc trừ sâu", "hoat_chat": "Cypermethrin", "doi_tuong_phong_tru": "Sâu đục thân, sâu cuốn lá"},
    {"ten_thuoc": "Carbendazim 50% SC", "loai_thuoc": "Thuốc trừ nấm", "hoat_chat": "Carbendazim", "doi_tuong_phong_tru": "Bệnh héo xanh, đạo ôn"},
]


def populate_data():
    db = SessionLocal()
    try:
        # Helper to get next ID
        def get_next_id(model_class):
            table_name = model_class.__tablename__
            result = db.execute(text(f"SELECT MAX(id) FROM {table_name}"))
            max_id = result.scalar()
            return (max_id or 0) + 1

        # Don't clear - just add if not exists
        existing_crops = {c.ten_cay for c in db.query(LoaiCayTrong).all()}
        
        # Add crop types
        crop_objects = []
        next_crop_id = get_next_id(LoaiCayTrong)
        
        for crop_data in CROP_TYPES:
            if crop_data["ten_cay"] not in existing_crops:
                crop = LoaiCayTrong(id=next_crop_id, **crop_data)
                db.add(crop)
                crop_objects.append(crop)
                next_crop_id += 1
        db.commit()
        
        # Get all crops for assignment
        all_crops = db.query(LoaiCayTrong).all()
        print(f"Total crop types: {len(all_crops)} ({len(crop_objects)} new)")
        
        # Add fertilizer types
        print("\n=== POPULATING FERTILIZER TYPES ===")
        existing_ferts = {f.ten_phan_bon for f in db.query(PhanBon).all()}
        fertilizer_objects = []
        next_fert_id = get_next_id(PhanBon)
        
        for fert_data in FERTILIZER_TYPES:
            if fert_data["ten_phan_bon"] not in existing_ferts:
                fert = PhanBon(id=next_fert_id, **fert_data)
                db.add(fert)
                fertilizer_objects.append(fert)
                next_fert_id += 1
        db.commit()
        
        all_fertilizers = db.query(PhanBon).all()
        print(f"Total fertilizer types: {len(all_fertilizers)} ({len(fertilizer_objects)} new)")
        
        # Add pesticide types
        print("\n=== POPULATING PESTICIDE TYPES ===")
        existing_pests = {p.ten_thuoc for p in db.query(ThuocBVTV).all()}
        pesticide_objects = []
        next_pest_id = get_next_id(ThuocBVTV)
        
        for pest_data in PESTICIDE_TYPES:
            if pest_data["ten_thuoc"] not in existing_pests:
                pest = ThuocBVTV(id=next_pest_id, **pest_data)
                db.add(pest)
                pesticide_objects.append(pest)
                next_pest_id += 1
        db.commit()
        
        all_pesticides = db.query(ThuocBVTV).all()
        print(f"Total pesticide types: {len(all_pesticides)} ({len(pesticide_objects)} new)")
        
        # Refresh to get IDs
        for obj in all_crops + all_fertilizers + all_pesticides:
            db.refresh(obj)
        
        # Refresh all objects from DB to ensure valid IDs / persistence
        all_crops = db.query(LoaiCayTrong).all()
        all_fertilizers = db.query(PhanBon).all()
        all_pesticides = db.query(ThuocBVTV).all()
        
        # Assign types to farms
        print("\n=== ASSIGNING TYPES TO FARMS ===")
        farms = db.query(VungTrong).all()
        print(f"Found {len(farms)} farms")
        
        updated_count = 0
        for farm in farms:
            # Assign random crop type if available
            if all_crops:
                farm.cay_trong_id = random.choice(all_crops).id
            
            # Assign random fertilizer type if available
            if all_fertilizers:
                farm.phan_bon_id = random.choice(all_fertilizers).id
            
            # Assign random pesticide type if available
            if all_pesticides:
                farm.thuoc_bvtv_id = random.choice(all_pesticides).id
            
            updated_count += 1
        
        db.commit()
        print(f"Assigned types to {updated_count} farms")
        
        # Verify distribution
        print("\n=== VERIFICATION ===")
        from sqlalchemy import func
        
        crop_dist = db.query(
            LoaiCayTrong.ten_cay, func.count(VungTrong.id)
        ).join(VungTrong).group_by(LoaiCayTrong.ten_cay).all()
        
        print("\nCrop distribution:")
        for crop_name, count in crop_dist:
            print(f"  {crop_name}: {count} farms")
        
        fert_dist = db.query(
            PhanBon.ten_phan_bon, func.count(VungTrong.id)
        ).join(VungTrong, VungTrong.phan_bon_id == PhanBon.id).group_by(PhanBon.ten_phan_bon).all()
        
        print("\nFertilizer distribution:")
        for fert_name, count in fert_dist:
            print(f"  {fert_name}: {count} farms")
        
        pest_dist = db.query(
            ThuocBVTV.ten_thuoc, func.count(VungTrong.id)
        ).join(VungTrong, VungTrong.thuoc_bvtv_id == ThuocBVTV.id).group_by(ThuocBVTV.ten_thuoc).all()
        
        print("\nPesticide distribution:")
        for pest_name, count in pest_dist:
            print(f"  {pest_name}: {count} farms")
        
        print("\n✅ Done!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    populate_data()
