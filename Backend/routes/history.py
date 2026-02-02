# Cultivation History Routes (Lịch sử canh tác)
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import date, datetime
from typing import Optional

from database import get_db
from models import User, VungTrong, LichSuCanhTac
from schemas import HistoryCreate, HistoryUpdate, HistoryResponse, PaginatedResponse
from utils.auth import get_current_active_user
from utils.pagination import paginate

router = APIRouter(prefix="/history", tags=["Lịch sử canh tác"])


@router.get("", response_model=PaginatedResponse[HistoryResponse])
async def list_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    vung_trong_id: Optional[int] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Lấy danh sách lịch sử canh tác
    
    - **vung_trong_id**: Lọc theo vùng trồng
    - **from_date**: Từ ngày (YYYY-MM-DD)
    - **to_date**: Đến ngày (YYYY-MM-DD)
    """
    query = db.query(LichSuCanhTac)
    
    # Permission check for vung_trong_id
    if current_user.role != "admin":
        if vung_trong_id:
            # Check ownership of the specific farm being filtered
            farm = db.query(VungTrong).filter(VungTrong.id == vung_trong_id).first()
            if not farm or farm.chu_so_huu_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to view history for this farm"
                )
        else:
             # Logic complex: if no specific farm filtered, limit query to ALL farms owned by user
             # Subquery or Join
             query = query.join(VungTrong).filter(VungTrong.chu_so_huu_id == current_user.id)

    # Apply filters
    if vung_trong_id:
        query = query.filter(LichSuCanhTac.vung_trong_id == vung_trong_id)
    
    if from_date:
        query = query.filter(LichSuCanhTac.ngay_thuc_hien >= from_date)
    
    if to_date:
        query = query.filter(LichSuCanhTac.ngay_thuc_hien <= to_date)
    
    # Order by date descending
    query = query.order_by(LichSuCanhTac.ngay_thuc_hien.desc())
    
    # Paginate
    result = paginate(query, page, page_size)
    
    return PaginatedResponse(**result)


@router.get("/{history_id}", response_model=HistoryResponse)
async def get_history(history_id: int, db: Session = Depends(get_db)):
    """
    Lấy chi tiết lịch sử canh tác
    
    - **history_id**: ID lịch sử
    """
    history = db.query(LichSuCanhTac).filter(LichSuCanhTac.id == history_id).first()
    
    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"History record with ID {history_id} not found"
        )
    
    return history


@router.post("", response_model=HistoryResponse, status_code=status.HTTP_201_CREATED)
async def create_history(
    history_data: HistoryCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Tạo lịch sử canh tác mới
    
    Requires: Authentication
    """
    # Check farm exists
    farm = db.query(VungTrong).filter(VungTrong.id == history_data.vung_trong_id).first()
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm with ID {history_data.vung_trong_id} not found"
        )
        
    # Check permission
    if current_user.role != "admin" and farm.chu_so_huu_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to add history to this farm"
        )
    
    # Create history record
    new_history = LichSuCanhTac(**history_data.model_dump())
    db.add(new_history)
    db.commit()
    db.refresh(new_history)
    
    return new_history


@router.put("/{history_id}", response_model=HistoryResponse)
async def update_history(
    history_id: int,
    history_data: HistoryUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Cập nhật lịch sử canh tác
    
    Requires: Authentication
    """
    history = db.query(LichSuCanhTac).filter(LichSuCanhTac.id == history_id).first()
    
    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"History record with ID {history_id} not found"
        )
        
    # Check permission logic via Farm
    farm = db.query(VungTrong).filter(VungTrong.id == history.vung_trong_id).first()
    if current_user.role != "admin" and farm.chu_so_huu_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to edit this history record"
        )
    
    # Update fields
    update_data = history_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(history, field, value)
    
    db.commit()
    db.refresh(history)
    
    return history


@router.delete("/{history_id}")
async def delete_history(
    history_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Xóa lịch sử canh tác
    
    Requires: Authentication
    """
    history = db.query(LichSuCanhTac).filter(LichSuCanhTac.id == history_id).first()
    
    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"History record with ID {history_id} not found"
        )
        
    # Check permission logic via Farm
    farm = db.query(VungTrong).filter(VungTrong.id == history.vung_trong_id).first()
    if current_user.role != "admin" and farm.chu_so_huu_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this history record"
        )
    
    db.delete(history)
    db.commit()
    
    return {"message": f"History record {history_id} deleted successfully"}
