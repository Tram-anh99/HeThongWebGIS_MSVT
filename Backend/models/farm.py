# Farm (Vùng trồng) Model
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from models.base import Base, TimestampMixin


class VungTrong(Base, TimestampMixin):
    """Model cho vùng trồng (farms)"""
    __tablename__ = "vung_trong"
    
    id = Column(Integer, primary_key=True, index=True)
    ma_vung = Column(String(50), unique=True, nullable=False, index=True)
    ten_vung = Column(String(200), nullable=False)
    dien_tich = Column(Numeric(10, 2))
    nguoi_dai_dien = Column(String(200))
    
    # Foreign Keys
    cay_trong_id = Column(Integer, ForeignKey("loai_cay_trong.id"))
    chu_so_huu_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Temporary denormalized fields (will be FK when boundaries imported)
    xa_name = Column(String(200))
    huyen_name = Column(String(200))
    tinh_name = Column(String(100))
    thi_truong_xuat_khau = Column(String(200))
    
    # GPS Coordinates (optional)
    latitude = Column(Numeric(10, 6), nullable=True)
    longitude = Column(Numeric(10, 6), nullable=True)
    
    # Relationships
    cay_trong = relationship("LoaiCayTrong", backref="vung_trong_list")
    lich_su = relationship("LichSuCanhTac", back_populates="vung_trong")
    vu_mua = relationship("VuMua", back_populates="vung_trong")
    bao_dong = relationship("BaoDong", back_populates="vung_trong")
    
    def __repr__(self):
        return f"<VungTrong(ma_vung='{self.ma_vung}', ten='{self.ten_vung}')>"
