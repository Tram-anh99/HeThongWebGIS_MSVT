"""
========== Comprehensive Data Import Script ==========
Import all data from Database/data folders with 3NF compliance
Author: HeThongWebGIS_MSVT
"""

import sys
import os
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, text
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Database connection
DATABASE_URL = "postgresql://anllen@localhost:5432/webgis_msvt"
engine = create_engine(DATABASE_URL)

DATA_DIR = Path(__file__).parent.parent / "data"


def clean_value(value, max_len=None):
    """Clean and validate value"""
    if pd.isna(value) or value == '' or value == 'nan':
        return None
    cleaned = str(value).strip()
    if max_len and len(cleaned) > max_len:
        return cleaned[:max_len]
    return cleaned


def import_phanbon():
    """Import phân bón data"""
    print("\n" + "=" * 70)
    print("IMPORTING: Phân Bón (Fertilizers)")
    print("=" * 70)
    
    file_path = DATA_DIR / "phanbon" / "PhanBonDuocSX_KD_SD.xlsx"
    
    if not file_path.exists():
        logger.warning(f"File not found: {file_path}")
        return False
    
    try:
        df = pd.read_excel(file_path)
        logger.info(f"Loaded {len(df)} rows from {file_path.name}")
        
        # Ensure table exists
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS phan_bon (
                    id SERIAL PRIMARY KEY,
                    ten_phan_bon VARCHAR(500),
                    thanh_phan TEXT,
                    nha_san_xuat VARCHAR(500),
                    lieu_luong_khuyen_nghi TEXT
                );
                TRUNCATE TABLE phanbon CASCADE;
            """))
        
        # Import data
        records = []
        for idx, row in df.iterrows():
            ten = clean_value(row.get('Tên phân bón'))
            if not ten:
                continue
            
            record = {
                'ten_phan_bon': ten,
                'thanh_phan': clean_value(row.get('Thành phần, hàm lượng đăng ký')),
                'nha_san_xuat': clean_value(row.get('Tổ chức, cá nhân đăng ký')),
                'lieu_luong_khuyen_nghi': clean_value(row.get('Thành phần, hàm lượng đăng ký'))
            }
            records.append(record)
        
        # Bulk insert
        if records:
            df_import = pd.DataFrame(records)
            df_import.to_sql('phan_bon', engine, if_exists='append', index=False)
            logger.info(f"✅ Imported {len(records)} phân bón")
            return True
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def import_thuoc_bvtv():
    """Import thuốc BVTV data"""
    print("\n" + "=" * 70)
    print("IMPORTING: Thuốc Bảo Vệ Thực Vật (Pesticides)")
    print("=" * 70)
    
    file_path = DATA_DIR / "thuocbaovethucvat" / "ThuocBaoVeThucVat.xlsx"
    
    if not file_path.exists():
        logger.warning(f"File not found: {file_path}")
        return False
    
    try:
        df = pd.read_excel(file_path)
        logger.info(f"Loaded {len(df)} rows from {file_path.name}")
        
        # Ensure table exists
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS thuoc_bvtv (
                    id SERIAL PRIMARY KEY,
                    ten_thuoc VARCHAR(500),
                    hoat_chat VARCHAR(500),
                    nha_san_xuat VARCHAR(500),
                    doi_tuong_phong_tru TEXT,
                    loai_thuoc VARCHAR(200)
                );
                TRUNCATE TABLE thuoc_bvtv CASCADE;
            """))
        
        # Import data
        records = []
        for idx, row in df.iterrows():
            hoat_chat = clean_value(row.get('Hoạt chất'))
            if not hoat_chat:
                continue
            
            record = {
                'ten_thuoc': clean_value(row.get('Tên thương phẩm')),
                'hoat_chat': hoat_chat,
                'nha_san_xuat': clean_value(row.get('Tổ chức đăng ký')),
                'doi_tuong_phong_tru': clean_value(row.get('Đối tượng phòng trừ')),
                'loai_thuoc': clean_value(row.get(' Loại thuốc bảo vệ thực vật'))
            }
            records.append(record)
        
        if records:
            df_import = pd.DataFrame(records)
            df_import.to_sql('thuoc_bvtv', engine, if_exists='append', index=False)
            logger.info(f"✅ Imported {len(records)} thuốc BVTV")
            return True
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def import_giong():
    """Import giống cây data"""
    print("\n" + "=" * 70)
    print("IMPORTING: Giống Cây (Seeds/Varieties)")
    print("=" * 70)
    
    file_path = DATA_DIR / "giong" / "giong_baoho.xlsx"
    
    if not file_path.exists():
        logger.warning(f"File not found: {file_path}")
        return False
    
    try:
        df = pd.read_excel(file_path)
        logger.info(f"Loaded {len(df)} rows from {file_path.name}")
        
        # Ensure table exists
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS giong_cay (
                    id SERIAL PRIMARY KEY,
                    ten_giong VARCHAR(500),
                    chu_so_huu VARCHAR(500),
                    ngay_dang_ky DATE,
                    tinh_trang VARCHAR(200)
                );
                TRUNCATE TABLE giong_cay CASCADE;
            """))
        
        # Import data
        records = []
        for idx, row in df.iterrows():
            ten_giong = clean_value(row.get('tengiong'))
            if not ten_giong:
                continue
            
            record = {
                'ten_giong': ten_giong,
                'chu_so_huu': clean_value(row.get('tenchusohuu')),
                'ngay_dang_ky': pd.to_datetime(row.get('ngaydk_bd_hieuluc'), errors='coerce'),
                'tinh_trang': clean_value(row.get('Tình trạng bằng'))
            }
            records.append(record)
        
        if records:
            df_import = pd.DataFrame(records)
            df_import.to_sql('giong_cay', engine, if_exists='append', index=False)
            logger.info(f"✅ Imported {len(records)} giống cây")
            return True
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def import_msvt_data():
    """Import MSVT data (vùng trồng, chủ sở hữu, thị trường)"""
    print("\n" + "=" * 70)
    print("IMPORTING: MSVT Data (Farms, Owners, Markets)")
    print("=" * 70)
    
    msvt_dir = DATA_DIR / "msvt"
    
    # 1. Import chủ sở hữu
    file_path = msvt_dir / "msvt_chusohuu.xlsx"
    if file_path.exists():
        try:
            df = pd.read_excel(file_path)
            logger.info(f"Loaded {len(df)} chủ sở hữu")
            
            with engine.begin() as conn:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS chu_so_huu (
                        id SERIAL PRIMARY KEY,
                        ho_ten VARCHAR(200),
                        cmnd VARCHAR(50),
                        dia_chi TEXT,
                        dien_thoai VARCHAR(50)
                    );
                    TRUNCATE TABLE chu_so_huu CASCADE;
                """))
            
            records = []
            for idx, row in df.iterrows():
                ho_ten = clean_value(row.get('hoten', row.get('Họ tên')))
                if ho_ten:
                    records.append({
                        'ho_ten': ho_ten,
                        'cmnd': clean_value(row.get('cmnd', row.get('CMND'))),
                        'dia_chi': clean_value(row.get('diachi', row.get('Địa chỉ'))),
                        'dien_thoai': clean_value(row.get('dienthoai', row.get('Điện thoại')))
                    })
            
            if records:
                pd.DataFrame(records).to_sql('chu_so_huu', engine, if_exists='append', index=False)
                logger.info(f"✅ Imported {len(records)} chủ sở hữu")
        except Exception as e:
            logger.error(f"❌ Error importing chủ sở hữu: {e}")
    
    # 2. Import vùng trồng
    file_path = msvt_dir / "msvt_thongtinvungtrong.xlsx"
    if file_path.exists():
        try:
            df = pd.read_excel(file_path)
            logger.info(f"Loaded {len(df)} vùng trồng")
            
            with engine.begin() as conn:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS vung_trong (
                        id SERIAL PRIMARY KEY,
                        ma_vung VARCHAR(50) UNIQUE,
                        ten_vung VARCHAR(200),
                        dien_tich NUMERIC(10,2),
                        chu_so_huu_id INTEGER,
                        trang_thai VARCHAR(100)
                    );
                    TRUNCATE TABLE vung_trong CASCADE;
                """))
            
            records = []
            for idx, row in df.iterrows():
                ma_vung = clean_value(row.get('mavung', row.get('Mã vùng')))
                if ma_vung:
                    records.append({
                        'ma_vung': ma_vung,
                        'ten_vung': clean_value(row.get('tenvung', row.get('Tên vùng'))),
                        'dien_tich': row.get('dientich', row.get('Diện tích')),
                        'chu_so_huu_id': row.get('chusohuu_ID'),
                        'trang_thai': clean_value(row.get('trangthai', row.get('Trạng thái')))
                    })
            
            if records:
                pd.DataFrame(records).to_sql('vung_trong', engine, if_exists='append', index=False)
                logger.info(f"✅ Imported {len(records)} vùng trồng")
        except Exception as e:
            logger.error(f"❌ Error importing vùng trồng: {e}")
    
    return True


def generate_summary():
    """Generate import summary"""
    print("\n" + "=" * 70)
    print("IMPORT SUMMARY")
    print("=" * 70)
    
    tables = ['phan_bon', 'thuoc_bvtv', 'giong_cay', 'chu_so_huu', 'vung_trong']
    
    with engine.connect() as conn:
        for table in tables:
            try:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                print(f"  {table:20s}: {count:>6,} records")
            except Exception:
                print(f"  {table:20s}: Table not found")
    
    print("=" * 70)


def main():
    """Main import function"""
    print("\n" + "=" * 80)
    print(" " * 20 + "COMPREHENSIVE DATA IMPORT")
    print(" " * 25 + "3NF Compliant")
    print("=" * 80)
    
    success = True
    
    # Import all datasets
    if not import_phanbon():
        success = False
    
    if not import_thuoc_bvtv():
        success = False
    
    if not import_giong():
        success = False
    
    if not import_msvt_data():
        success = False
    
    # Generate summary
    generate_summary()
    
    print("\n" + "=" * 80)
    if success:
        print("✅ DATA IMPORT COMPLETED SUCCESSFULLY!")
    else:
        print("⚠️  IMPORT COMPLETED WITH SOME WARNINGS")
    print("=" * 80)
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
