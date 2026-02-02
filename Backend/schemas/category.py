# Category Schemas
from pydantic import BaseModel
from typing import Optional


class CategoryBase(BaseModel):
    """Generic category base"""
    id: int
    
    class Config:
        from_attributes = True


class CropTypeResponse(CategoryBase):
    """Loại cây trồng response"""
    ten_cay: str
    ten_khoa_hoc: Optional[str] = None


class ActivityTypeResponse(CategoryBase):
    """Loại hoạt động response"""
    ten_hoat_dong: str
    mo_ta: Optional[str] = None


class FertilizerResponse(CategoryBase):
    """Phân bón response"""
    ten_phan_bon: Optional[str] = None
    nha_san_xuat: Optional[str] = None
    thanh_phan: Optional[str] = None
    lieu_luong_khuyen_nghi: Optional[str] = None


class PesticideResponse(CategoryBase):
    """Thuốc BVTV response"""
    ten_thuoc: Optional[str] = None
    hoat_chat: Optional[str] = None
    nha_san_xuat: Optional[str] = None
    doi_tuong_phong_tru: Optional[str] = None
    loai_thuoc: Optional[str] = None


class SeedResponse(CategoryBase):
    """Giống cây response"""
    ten_giong: Optional[str] = None
    chu_so_huu: Optional[str] = None
    tinh_trang: Optional[str] = None
