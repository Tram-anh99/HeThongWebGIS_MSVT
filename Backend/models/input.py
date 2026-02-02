# Input Models - Phân bón, Thuốc BVTV, Giống cây
from sqlalchemy import Column, Integer, String, Text, Date
from models.base import Base


class PhanBon(Base):
    """Phân bón (Fertilizers)"""
    __tablename__ = "phan_bon"
    
    id = Column(Integer, primary_key=True, index=True)
    ten_phan_bon = Column(String(500))
    nha_san_xuat = Column(String(500))
    thanh_phan = Column(Text)
    lieu_luong_khuyen_nghi = Column(Text)
    
    def __repr__(self):
        return f"<PhanBon(id={self.id}, ten='{self.ten_phan_bon}')>"


class ThuocBVTV(Base):
    """Thuốc bảo vệ thực vật (Pesticides)"""
    __tablename__ = "thuoc_bvtv"
    
    id = Column(Integer, primary_key=True, index=True)
    ten_thuoc = Column(String(500))
    hoat_chat = Column(String(500))
    nha_san_xuat = Column(String(500))
    doi_tuong_phong_tru = Column(Text)
    loai_thuoc = Column(String(200))
    
    def __repr__(self):
        return f"<ThuocBVTV(id={self.id}, ten='{self.ten_thuoc}')>"


class GiongCay(Base):
    """Giống cây (Seed varieties)"""
    __tablename__ = "giong_cay"
    
    id = Column(Integer, primary_key=True, index=True)
    ten_giong = Column(String(500))
    chu_so_huu = Column(String(500))
    ngay_dang_ky = Column(Date)
    tinh_trang = Column(String(200))
    
    def __repr__(self):
        return f"<GiongCay(id={self.id}, ten='{self.ten_giong}')>"
