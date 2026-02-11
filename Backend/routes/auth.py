# Authentication Routes
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from database import get_db
from models import User
from schemas import UserCreate, UserResponse, UserLogin, Token
from utils.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user,
    get_current_active_user
)
from config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


# Dependency to require admin role
async def require_admin(current_user: User = Depends(get_current_active_user)):
    """
    Dependency that requires the current user to have admin role
    
    Raises HTTPException if user is not an admin
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: admin role required"
        )
    return current_user


# Dependency to require admin or manager role
async def require_manager_or_admin(current_user: User = Depends(get_current_active_user)):
    """
    Dependency that requires the current user to have admin or manager role
    
    Raises HTTPException if user is neither admin nor manager
    """
    if current_user.role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: admin or manager role required"
        )
    return current_user



@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Đăng ký người dùng mới
    
    - **username**: Tên đăng nhập (unique)
    - **email**: Email (unique)
    - **password**: Mật khẩu (min 6 ký tự)
    - **full_name**: Họ tên đầy đủ
    - **role**: Vai trò (admin, farmer, viewer)
    """
    # Check if username exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
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


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Đăng nhập và nhận JWT token
    
    - **username**: Tên đăng nhập
    - **password**: Mật khẩu
    """
    # Find user
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id},
        expires_delta=access_token_expires
    )
    
    # Return token and user info
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm(user)
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """
    Lấy thông tin người dùng hiện tại
    
    Requires: Bearer token
    """
    return current_user


@router.post("/logout")
async def logout():
    """
    Đăng xuất (client-side token removal)
    
    Note: JWT tokens are stateless, logout is handled on client side
    """
    return {"message": "Successfully logged out"}
