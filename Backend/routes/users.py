# User Management Routes (Admin only)
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from models import User
from schemas import UserCreate, UserUpdate, UserResponse, PaginatedResponse
from utils.auth import get_current_active_user, get_password_hash
from utils.pagination import paginate
from utils.permission import get_province_filter, is_manager_or_admin

router = APIRouter(prefix="/users", tags=["Quản lý Người dùng"])


@router.get("", response_model=PaginatedResponse[UserResponse])
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    role: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Lấy danh sách người dùng (Admin and Manager)
    Managers can only see farmers in their province
    """
    if not is_manager_or_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requires admin or manager privileges"
        )

    query = db.query(User)
    
    # Province filtering for managers
    if current_user.role == "manager":
        # Managers only see farmers from their province
        # We need to join with VungTrong to filter by province
        province_filter = get_province_filter(current_user)
        if province_filter:
            from models.farm import VungTrong
            # Get farmer IDs who own farms in manager's province
            farmer_ids = db.query(VungTrong.chu_so_huu_id).filter(
                VungTrong.tinh_name == province_filter,
                VungTrong.chu_so_huu_id.isnot(None)
            ).distinct().all()
            farmer_ids = [f[0] for f in farmer_ids]
            # Filter to only show farmers in their province
            query = query.filter(
                User.role == "farmer",
                User.id.in_(farmer_ids)
            )
    
    # Filters
    if search:
        query = query.filter(
            (User.username.ilike(f"%{search}%")) |
            (User.full_name.ilike(f"%{search}%")) |
            (User.email.ilike(f"%{search}%"))
        )
    
    if role:
        query = query.filter(User.role == role)
        
    # Order by ID
    query = query.order_by(User.id.desc())
    
    # Paginate
    result = paginate(query, page, page_size)
    return PaginatedResponse(**result)


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Tạo người dùng mới (Admin and Manager)
    Managers can only create farmer accounts in their province
    """
    if not is_manager_or_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requires admin or manager privileges"
        )
        
    # Check exists
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
        
    # Create
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        password_hash=hashed_password,
        role=user_data.role or "farmer",
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Cập nhật người dùng (Admin only)
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requires admin privileges"
        )
        
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Update fields
    update_data = user_data.model_dump(exclude_unset=True)
    
    if "password" in update_data and update_data["password"]:
        update_data["password_hash"] = get_password_hash(update_data["password"])
        del update_data["password"]
        
    for field, value in update_data.items():
        setattr(user, field, value)
        
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Xóa người dùng (Admin only)
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requires admin privileges"
        )
        
    # Prevent deleting self
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
        
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Before deleting user, nullify farm ownership to avoid foreign key constraint
    from models.farm import VungTrong
    db.query(VungTrong).filter(VungTrong.chu_so_huu_id == user_id).update(
        {VungTrong.chu_so_huu_id: None}
    )
    db.flush()  # Ensure update is applied before delete
        
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}


