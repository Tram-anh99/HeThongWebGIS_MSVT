# Category Routes (Danh mục)
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import LoaiCayTrong, LoaiHoatDong, PhanBon, ThuocBVTV, GiongCay
from schemas import (
    CropTypeResponse,
    ActivityTypeResponse,
    FertilizerResponse,
    PesticideResponse,
    SeedResponse
)

router = APIRouter(prefix="/categories", tags=["Danh mục"])


@router.get("/crops", response_model=List[CropTypeResponse])
async def get_crop_types(db: Session = Depends(get_db)):
    """Lấy danh sách loại cây trồng"""
    crops = db.query(LoaiCayTrong).all()
    return crops


@router.get("/activities", response_model=List[ActivityTypeResponse])
async def get_activity_types(db: Session = Depends(get_db)):
    """Lấy danh sách loại hoạt động canh tác"""
    activities = db.query(LoaiHoatDong).all()
    return activities


@router.get("/fertilizers", response_model=List[FertilizerResponse])
async def get_fertilizers(limit: int = 100, db: Session = Depends(get_db)):
    """Lấy danh sách phân bón được phép sử dụng"""
    fertilizers = db.query(PhanBon).limit(limit).all()
    return fertilizers


@router.get("/pesticides", response_model=List[PesticideResponse])
async def get_pesticides(limit: int = 100, db: Session = Depends(get_db)):
    """Lấy danh sách thuốc BVTV được phép sử dụng"""
    pesticides = db.query(ThuocBVTV).limit(limit).all()
    return pesticides


@router.get("/seeds", response_model=List[SeedResponse])
async def get_seeds(limit: int = 100, db: Session = Depends(get_db)):
    """Lấy danh sách giống cây bảo hộ"""
    seeds = db.query(GiongCay).limit(limit).all()
    return seeds
