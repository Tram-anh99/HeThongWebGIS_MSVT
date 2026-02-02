# Farm Routes (Vùng trồng)
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from models import User, VungTrong, LichSuCanhTac
from schemas import FarmCreate, FarmUpdate, FarmResponse, FarmWithHistory, HistoryResponse, PaginatedResponse
from utils.auth import get_current_active_user
from utils.pagination import paginate

router = APIRouter(prefix="/farms", tags=["Vùng trồng"])


@router.get("", response_model=PaginatedResponse[FarmResponse])
async def list_farms(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    tinh: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Lấy danh sách vùng trồng
    
    - **page**: Trang (default: 1)
    - **page_size**: Số lượng/trang (default: 20, max: 100)
    - **search**: Tìm kiếm theo mã vùng hoặc tên
    - **tinh**: Lọc theo tỉnh
    """
    query = db.query(VungTrong)
    
    # Filter by user role
    if current_user.role != "admin":
        query = query.filter(VungTrong.chu_so_huu_id == current_user.id)
    
    # Apply filters
    if search:
        query = query.filter(
            (VungTrong.ma_vung.ilike(f"%{search}%")) |
            (VungTrong.ten_vung.ilike(f"%{search}%"))
        )
    
    if tinh:
        query = query.filter(VungTrong.tinh_name.ilike(f"%{tinh}%"))
    
    # Order by ID
    query = query.order_by(VungTrong.id.desc())
    
    # Paginate
    result = paginate(query, page, page_size)
    
    return PaginatedResponse(**result)


@router.get("/{farm_id}", response_model=FarmResponse)
async def get_farm(
    farm_id: int, 
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Lấy chi tiết vùng trồng
    
    - **farm_id**: ID vùng trồng
    """
    farm = db.query(VungTrong).filter(VungTrong.id == farm_id).first()
    
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm with ID {farm_id} not found"
        )
        
    # Check permission
    if current_user.role != "admin" and farm.chu_so_huu_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this farm"
        )
    
    return farm


@router.post("", response_model=FarmResponse, status_code=status.HTTP_201_CREATED)
async def create_farm(
    farm_data: FarmCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Tạo vùng trồng mới
    
    Requires: Authentication
    """
    # Check if ma_vung exists
    existing = db.query(VungTrong).filter(VungTrong.ma_vung == farm_data.ma_vung).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Farm with code {farm_data.ma_vung} already exists"
        )
    
    # Create farm
    new_farm = VungTrong(**farm_data.model_dump())
    db.add(new_farm)
    db.commit()
    db.refresh(new_farm)
    
    return new_farm


@router.put("/{farm_id}", response_model=FarmResponse)
async def update_farm(
    farm_id: int,
    farm_data: FarmUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Cập nhật thông tin vùng trồng
    
    Requires: Authentication
    """
    farm = db.query(VungTrong).filter(VungTrong.id == farm_id).first()
    
    # Check permission
    if current_user.role != "admin" and farm.chu_so_huu_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this farm"
        )
    
    # Update fields
    update_data = farm_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(farm, field, value)
    
    db.commit()
    db.refresh(farm)
    
    return farm


@router.delete("/{farm_id}")
async def delete_farm(
    farm_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Xóa vùng trồng
    
    Requires: Authentication (Admin only)
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can delete farms"
        )
    
    farm = db.query(VungTrong).filter(VungTrong.id == farm_id).first()
    
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm with ID {farm_id} not found"
        )
    
    db.delete(farm)
    db.commit()
    
    return {"message": f"Farm {farm.ma_vung} deleted successfully"}


@router.get("/{farm_id}/history", response_model=List[HistoryResponse])
async def get_farm_history(
    farm_id: int,
    db: Session = Depends(get_db)
):
    """
    Lấy lịch sử canh tác của vùng trồng
    
    - **farm_id**: ID vùng trồng
    """
    # Check farm exists
    farm = db.query(VungTrong).filter(VungTrong.id == farm_id).first()
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm with ID {farm_id} not found"
        )
    
    # Get history
    history = db.query(LichSuCanhTac)\
        .filter(LichSuCanhTac.vung_trong_id == farm_id)\
        .order_by(LichSuCanhTac.ngay_thuc_hien.desc())\
        .all()
    
    return history
