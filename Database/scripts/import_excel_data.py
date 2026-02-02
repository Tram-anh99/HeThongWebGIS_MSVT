"""
========== Import Data với 3NF Compliance ==========
Import dữ liệu từ Excel với normalization (3NF)
Author: HeThongWebGIS_MSVT
"""

import sys
import os
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../Backend'))
sys.path.insert(0, backend_path)

import pandas as pd
from database import SessionLocal
from models import *
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent / "data"


def clean_string(value, max_len=500):
    """Clean and truncate string"""
    if pd.isna(value) or value == '':
        return None
    return str(value).strip()[:max_len]


def import_phanbon_simple():
    """Import phân bón - normalized approach"""
    print("\n" + "=" * 70)
    print("Importing Fertilizer Data (3NF Compliant)")
    print("=" * 70)
    
    db = SessionLocal()
    
    try:
        # Clear data
        db.query(PhanBon).delete()
        db.commit()
        
        # Import from simplest/most normalized file first
        phanbon_dir = DATA_DIR / "phanbon"
        
        # Try different files
        files_to_try = [
            "PhanBonDuocSX_KD_SD.xlsx",
            "DanhMuc_PhanBon_DuocPhep_LuuHanh.xlsx",
            "Thongtu85.xls",
        ]
        
        for filename in files_to_try:
            file_path = phanbon_dir / filename
            if not file_path.exists():
                continue
                
            print(f"\n📂 Trying {filename}...")
            
            try:
                # Read Excel file
                df = pd.read_excel(file_path)
                print(f"   Loaded {len(df)} rows, {len(df.columns)} columns")
                print(f"   Columns: {list(df.columns)[:10]}")
                
                # Find relevant columns (fuzzy matching)
                col_map = {}
                for col in df.columns:
                    col_lower =str(col).lower()
                    if 'tên' in col_lower and 'phân' in col_lower:
                        col_map['ten_phan_bon'] = col
                    elif 'nhà' in col_lower and 'sản' in col_lower:
                        col_map['nha_san_xuat'] = col
                    elif 'liều' in col_lower or 'lượng' in col_lower:
                        col_map['lieu_luong'] = col
                
                if not col_map.get('ten_phan_bon'):
                    print("   ⚠️  Could not find 'Tên phân bón' column, skipping...")
                    continue
                
                print(f"   Mapped columns: {col_map}")
                
                # Import data
                count = 0
                for idx, row in df.iterrows():
                    ten = clean_string(row.get(col_map.get('ten_phan_bon')))
                    if not ten:
                        continue
                    
                    phan_bon = PhanBon(
                        ten_phan_bon=ten,
                        nha_san_xuat=clean_string(row.get(col_map.get('nha_san_xuat', ''))) if col_map.get('nha_san_xuat') else None,
                        lieu_luong_khuyen_nghi=clean_string(row.get(col_map.get('lieu_luong', ''))) if col_map.get('lieu_luong') else None
                    )
                    db.add(phan_bon)
                    count += 1
                    
                    if count % 100 == 0:
                        db.commit()
                        print(f"      Imported {count}...")
                
                db.commit()
                print(f"   ✅ Successfully imported {count} phân bón from {filename}")
                break  # Success, stop trying other files
                
            except Exception as e:
                logger.warning(f"   ❌ Failed to import from {filename}: {e}")
                db.rollback()
                continue
        
        # Verify
        total = db.query(PhanBon).count()
        print(f"\n📊 Total in database: {total}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
    finally:
        db.close()


def import_giong_simple():
    """Import giống cây - normalized"""
    print("\n" + "=" * 70)
    print("Importing Seed Data (3NF Compliant)")
    print("=" * 70)
    
    db = SessionLocal()
    
    try:
        db.query(GiongCay).delete()
        db.commit()
        
        giong_dir = DATA_DIR / "giong"
        file_path = giong_dir / "giong_baoho.xlsx"
        
        if file_path.exists():
            print(f"\n📂 Importing from giong_baoho.xlsx...")
            df = pd.read_excel(file_path)
            print(f"   Loaded {len(df)} rows")
            print(f"   Columns: {list(df.columns)}")
            
            count = 0
            for idx, row in df.iterrows():
                ten_giong = clean_string(row.get('tengiong', row.get('Tên giống', '')))
                if not ten_giong:
                    continue
                
                giong = GiongCay(
                    ten_giong=ten_giong,
                    nguon_goc=clean_string(row.get('tenchusohuu', row.get('Nguồn gốc', '')))
                )
                db.add(giong)
                count += 1
                
                if count % 50 == 0:
                    db.commit()
                    print(f"      Imported {count}...")
            
            db.commit()
            print(f"   ✅ Imported {count} giống cây")
            
            total = db.query(GiongCay).count()
            print(f"\n📊 Total: {total}")
            
            return True
        else:
            print("   ⚠️  File not found")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
    finally:
        db.close()


def main():
    """Main import function"""
    print("=" * 70)
    print("Importing Data with 3NF Compliance")
    print("=" * 70)
    
    success = True
    
    # Import phân bón
    if not import_phanbon_simple():
        print("⚠️  Phan bon import had issues")
        success = False
    
    # Import giống
    if not import_giong_simple():
        print("⚠️  Giong import had issues")
        success = False
    
    print("\n" + "=" * 70)
    if success:
        print("✅ Data import completed!")
    else:
        print("⚠️  Some imports had issues, but continuing...")
    print("=" * 70)
    
    # Show summary
    db = SessionLocal()
    print("\n📊 Final Summary:")
    print(f"   - Phân bón: {db.query(PhanBon).count()}")
    print(f"   - Giống cây: {db.query(GiongCay).count()}")
    print(f"   - Loại cây trồng: {db.query(LoaiCayTrong).count()}")
    print(f"   - Users: {db.query(User).count()}")
    db.close()
    
    return success


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
