# QR Code Routes
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from database import get_db
from models import VungTrong, LichSuCanhTac
from utils.qrcode_gen import generate_farm_qr_code
from config import settings

router = APIRouter(prefix="/qr", tags=["QR Code"])


@router.get("/generate/{ma_vung}")
async def generate_qr(ma_vung: str, db: Session = Depends(get_db)):
    """
    Generate QR code cho vùng trồng
    
    Returns: PNG image
    """
    # Check if farm exists
    farm = db.query(VungTrong).filter(VungTrong.ma_vung == ma_vung).first()
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm with code {ma_vung} not found"
        )
    
    # Generate QR code with frontend URL
    qr_image = generate_farm_qr_code(ma_vung, base_url=settings.FRONTEND_URL)
    
    return StreamingResponse(qr_image, media_type="image/png")


@router.get("/trace/{ma_vung}")
async def trace_farm(ma_vung: str, db: Session = Depends(get_db)):
    """
    Truy xuất nguồn gốc vùng trồng (Public endpoint)
    
    - **ma_vung**: Mã vùng trồng
    
    Returns: Farm info + cultivation history
    """
    # Get farm
    farm = db.query(VungTrong).filter(VungTrong.ma_vung == ma_vung).first()
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm with code {ma_vung} not found"
        )
    
    # Get history
    history = db.query(LichSuCanhTac)\
        .filter(LichSuCanhTac.vung_trong_id == farm.id)\
        .order_by(LichSuCanhTac.ngay_thuc_hien.desc())\
        .all()
    
    return {
        "farm": {
            "ma_vung": farm.ma_vung,
            "ten_vung": farm.ten_vung,
            "dien_tich": float(farm.dien_tich) if farm.dien_tich else None,
            "nguoi_dai_dien": farm.nguoi_dai_dien,
            "xa": farm.xa_name,
            "huyen": farm.huyen_name,
            "tinh": farm.tinh_name,
            "thi_truong_xuat_khau": farm.thi_truong_xuat_khau
        },
        "history": [
            {
                "ngay_thuc_hien": h.ngay_thuc_hien.isoformat() if h.ngay_thuc_hien else None,
                "chi_tiet": h.chi_tiet,
                "nguoi_thuc_hien": h.nguoi_thuc_hien,
                "lieu_luong": h.lieu_luong,
                "don_vi": h.don_vi
            }
            for h in history
        ],
        "total_activities": len(history)
    }
