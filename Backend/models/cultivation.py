# Cultivation Models - Lịch sử canh tác, Vụ mùa
from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from models.base import Base, TimestampMixin


class VuMua(Base):
    """Vụ mùa (Seasons/Crops)"""
    __tablename__ = "vu_mua"
    
    id = Column(Integer, primary_key=True, index=True)
    ten_vu = Column(String(200), nullable=False)
    vung_trong_id = Column(Integer, ForeignKey("vung_trong.id", ondelete="CASCADE"))
    ngay_bat_dau = Column(Date)
    ngay_ket_thuc = Column(Date)
    trang_thai = Column(String(100))
    ghi_chu = Column(Text)
    
    # Relationships
    vung_trong = relationship("VungTrong", back_populates="vu_mua")
    
    def __repr__(self):
        return f"<VuMua(id={self.id}, ten='{self.ten_vu}')>"


class LichSuCanhTac(Base, TimestampMixin):
    """Lịch sử canh tác (Cultivation history)"""
    __tablename__ = "lich_su_canh_tac"
    
    id = Column(Integer, primary_key=True, index=True)
    vung_trong_id = Column(Integer, ForeignKey("vung_trong.id", ondelete="CASCADE"))
    vu_mua_id = Column(Integer, ForeignKey("vu_mua.id"))
    loai_hoat_dong_id = Column(Integer, ForeignKey("loai_hoat_dong.id"))
    
    ngay_thuc_hien = Column(Date, nullable=False)
    chi_tiet = Column(Text)
    nguoi_thuc_hien = Column(String(200))
    
    # Optional references to inputs used
    phan_bon_id = Column(Integer, ForeignKey("phan_bon.id"))
    thuoc_bvtv_id = Column(Integer, ForeignKey("thuoc_bvtv.id", ondelete="SET NULL"))
    giong_id = Column(Integer, ForeignKey("giong_cay.id", ondelete="SET NULL"))
    
    lieu_luong = Column(String(200))
    don_vi = Column(String(100))
    
    # Relationships
    vung_trong = relationship("VungTrong", back_populates="lich_su")
    vu_mua = relationship("VuMua")
    loai_hoat_dong = relationship("LoaiHoatDong")
    phan_bon = relationship("PhanBon")
    thuoc_bvtv = relationship("ThuocBVTV")
    giong = relationship("GiongCay")
    
    def __repr__(self):
        return f"<LichSuCanhTac(id={self.id}, ngay='{self.ngay_thuc_hien}')>"
