# Schemas __init__.py - Export all schemas
from schemas.common import SuccessResponse, PaginatedResponse, ErrorResponse
from schemas.user import (
    UserCreate, UserUpdate, UserResponse, UserLogin, Token, TokenData
)
from schemas.farm import FarmCreate, FarmUpdate, FarmResponse, FarmWithHistory
from schemas.cultivation import (
    SeasonCreate, SeasonResponse,
    HistoryCreate, HistoryUpdate, HistoryResponse
)
from schemas.category import (
    CropTypeResponse, ActivityTypeResponse,
    FertilizerResponse, PesticideResponse, SeedResponse
)

__all__ = [
    # Common
    "SuccessResponse",
    "PaginatedResponse",
    "ErrorResponse",
    # User
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserLogin",
    "Token",
    "TokenData",
    # Farm
    "FarmCreate",
    "FarmUpdate",
    "FarmResponse",
    "FarmWithHistory",
    # Cultivation
    "SeasonCreate",
    "SeasonResponse",
    "HistoryCreate",
    "HistoryUpdate",
    "HistoryResponse",
    # Categories
    "CropTypeResponse",
    "ActivityTypeResponse",
    "FertilizerResponse",
    "PesticideResponse",
    "SeedResponse",
]
