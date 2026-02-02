# Database Backup Information

## Latest Backup

**Date:** $(date +"%Y-%m-%d %H:%M:%S")  
**Database:** webgis_msvt  
**PostgreSQL Version:** 17.5

---

## Backup Contents

### Data Tables (with records)
- `phan_bon`: 2,095 phân bón
- `thuoc_bvtv`: 4,572 thuốc BVTV
- `giong_cay`: 924 giống cây
- `chu_so_huu`: 350 chủ sở hữu
- `vung_trong`: 181 vùng trồng
- `loai_cay_trong`: 9 loại cây
- `thi_truong`: 13 thị trường
- `loai_hoat_dong`: 6 hoạt động
- `users`: 4 người dùng

### Structure Tables (empty - for spatial data)
- `tinh`, `huyen`, `xa` - Administrative boundaries
- `co_so_phan_bon`, `co_so_thuoc_bvtv` - Facilities
- `vu_mua`, `lich_su_canh_tac`, `bao_dong` - Operations

### Foreign Keys
- Total: 17 FK constraints
- All relationships properly established
- 3NF compliant

---

## Restore Instructions

To restore this backup:

```bash
# Method 1: Using psql
export PATH="/Applications/Postgres.app/Contents/Versions/latest/bin:$PATH"
psql -U anllen -d webgis_msvt_restored -f backup_file.sql

# Method 2: Create new database and restore
createdb -U anllen webgis_msvt_restored
psql -U anllen -d webgis_msvt_restored -f backup_file.sql
```

---

## Notes

- Backup includes full schema (tables, indexes, constraints)
- All data is included
- PostGIS extension settings included
- No ownership or privileges (use --no-owner --no-privileges)

---

**Backup Location:** `/Database/backups/`
