# Farm Schemas (Vùng trồng)
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class FarmBase(BaseModel):
    """Base farm schema"""
    ma_vung: str = Field(..., max_length=50)
    ten_vung: str = Field(..., max_length=200)
    dien_tich: Optional[Decimal] = None
    nguoi_dai_dien: Optional[str] = None
    cay_trong_id: Optional[int] = None
    xa_name: Optional[str] = None
    huyen_name: Optional[str] = None
    tinh_name: Optional[str] = None
    thi_truong_xuat_khau: Optional[str] = None
    chu_so_huu_id: Optional[int] = None
    # GPS Coordinates
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None


class FarmCreate(FarmBase):
    """Schema for creating farm"""
    pass


class FarmUpdate(BaseModel):
    """Schema for updating farm"""
    ten_vung: Optional[str] = None
    dien_tich: Optional[Decimal] = None
    nguoi_dai_dien: Optional[str] = None
    cay_trong_id: Optional[int] = None
    xa_name: Optional[str] = None
    huyen_name: Optional[str] = None
    tinh_name: Optional[str] = None
    thi_truong_xuat_khau: Optional[str] = None
    chu_so_huu_id: Optional[int] = None
    # GPS Coordinates
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None


class FarmResponse(FarmBase):
    """Schema for farm response"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class FarmWithHistory(FarmResponse):
    """Farm with cultivation history"""
    lich_su_count: int = 0
    vu_mua_count: int = 0
