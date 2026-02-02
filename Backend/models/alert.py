# Alert Model - Báo động
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from models.base import Base


class BaoDong(Base):
    """Báo động vùng canh tác (Alerts)"""
    __tablename__ = "bao_dong"
    
    id = Column(Integer, primary_key=True, index=True)
    vung_trong_id = Column(Integer, ForeignKey("vung_trong.id", ondelete="CASCADE"))
    loai_bao_dong = Column(String(100))  # dich_benh, thien_tai, etc.
    muc_do = Column(String(50))  # cao, trung_binh, thap
    tieu_de = Column(String(200))
    noi_dung = Column(Text)
    ngay_tao = Column(DateTime)
    trang_thai = Column(String(100))  # chua_giai_quyet, dang_xu_ly, da_giai_quyet
    ngay_giai_quyet = Column(DateTime)
    
    # Relationships
    vung_trong = relationship("VungTrong", back_populates="bao_dong")
    
    def __repr__(self):
        return f"<BaoDong(id={self.id}, loai='{self.loai_bao_dong}')>"
