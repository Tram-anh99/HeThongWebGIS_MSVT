# Category Models - Loại cây trồng, Loại hoạt động
from sqlalchemy import Column, Integer, String, Text
from models.base import Base


class LoaiCayTrong(Base):
    """Loại cây trồng (Crop types)"""
    __tablename__ = "loai_cay_trong"
    
    id = Column(Integer, primary_key=True)
    ten_cay = Column(String(200), nullable=False)
    ten_khoa_hoc = Column(String(300))
    
    def __repr__(self):
        return f"<LoaiCayTrong(id={self.id}, ten='{self.ten_cay}')>"


class LoaiHoatDong(Base):
    """Loại hoạt động canh tác (Activity types)"""
    __tablename__ = "loai_hoat_dong"
    
    id = Column(Integer, primary_key=True, index=True)
    ten_hoat_dong = Column(String(200), nullable=False)
    mo_ta = Column(Text)
    
    def __repr__(self):
        return f"<LoaiHoatDong(id={self.id}, ten='{self.ten_hoat_dong}')>"
