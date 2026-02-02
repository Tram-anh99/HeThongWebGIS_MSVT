"""
========== Configuration Settings ==========
Quản lý cấu hình hệ thống sử dụng Pydantic Settings
Author: HeThongWebGIS_MSVT
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """
    Class quản lý cấu hình ứng dụng
    
    Đọc từ environment variables hoặc file .env
    """
    
    # ========== API Settings ==========
    API_TITLE: str = "WebGIS MSVT API"
    API_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # ========== Database Settings ==========
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "webgis_msvt"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_SCHEMA: str = "public"
    
    @property
    def DATABASE_URL(self) -> str:
        """Tạo database connection string"""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    # ========== CORS Settings ==========
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Convert CORS origins string thành list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    # ========== JWT Authentication Settings ==========
    JWT_SECRET_KEY: str = "your-secret-key-change-this-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # ========== Upload Settings ==========
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Tạo instance settings global
settings = Settings()
