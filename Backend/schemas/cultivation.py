# Cultivation Schemas (Lịch sử canh tác, Vụ mùa)
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date


class SeasonBase(BaseModel):
    """Base season schema (Vụ mùa)"""
    ten_vu: str = Field(..., max_length=200)
    vung_trong_id: int
    ngay_bat_dau: Optional[date] = None
    ngay_ket_thuc: Optional[date] = None
    trang_thai: Optional[str] = None
    ghi_chu: Optional[str] = None


class SeasonCreate(SeasonBase):
    """Schema for creating season"""
    pass


class SeasonResponse(SeasonBase):
    """Schema for season response"""
    id: int
    
    class Config:
        from_attributes = True


class HistoryBase(BaseModel):
    """Base cultivation history schema"""
    vung_trong_id: int
    vu_mua_id: Optional[int] = None
    loai_hoat_dong_id: Optional[int] = None
    ngay_thuc_hien: date
    chi_tiet: Optional[str] = None
    nguoi_thuc_hien: Optional[str] = None
    phan_bon_id: Optional[int] = None
    thuoc_bvtv_id: Optional[int] = None
    giong_id: Optional[int] = None
    lieu_luong: Optional[str] = None
    don_vi: Optional[str] = None


class HistoryCreate(HistoryBase):
    """Schema for creating history record"""
    pass


class HistoryUpdate(BaseModel):
    """Schema for updating history"""
    vu_mua_id: Optional[int] = None
    loai_hoat_dong_id: Optional[int] = None
    ngay_thuc_hien: Optional[date] = None
    chi_tiet: Optional[str] = None
    nguoi_thuc_hien: Optional[str] = None
    phan_bon_id: Optional[int] = None
    thuoc_bvtv_id: Optional[int] = None
    giong_id: Optional[int] = None
    lieu_luong: Optional[str] = None
    don_vi: Optional[str] = None


class HistoryResponse(HistoryBase):
    """Schema for history response"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
