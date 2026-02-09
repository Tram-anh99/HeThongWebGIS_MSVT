# User Model
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from models.base import Base, TimestampMixin
from datetime import datetime


class User(Base, TimestampMixin):
    """Model cho người dùng hệ thống"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(200), unique=True, nullable=False, index=True)
    full_name = Column(String(200))
    password_hash = Column(String(200), nullable=False)
    role = Column(String(50), default="farmer")  # admin, manager, customs, farmer
    province_code = Column(String(10), nullable=True)  # For manager role: scope to specific province
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"
