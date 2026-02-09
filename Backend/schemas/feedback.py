# Feedback Schemas
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class FeedbackBase(BaseModel):
    """Base feedback schema"""
    subject: str = Field(..., min_length=5, max_length=200)
    message: str = Field(..., min_length=10)
    category: Optional[str] = "other"  # bug, feature_request, question, other


class FeedbackCreate(FeedbackBase):
    """Schema for creating feedback"""
    pass


class FeedbackUpdate(BaseModel):
    """Schema for updating feedback"""
    subject: Optional[str] = Field(None, min_length=5, max_length=200)
    message: Optional[str] = Field(None, min_length=10)
    category: Optional[str] = None
    status: Optional[str] = None  # Admin can update status
    admin_response: Optional[str] = None  # Admin can add response


class FeedbackResponse(FeedbackBase):
    """Schema for feedback response"""
    id: int
    user_id: int
    status: str
    admin_response: Optional[str] = None
    responded_by: Optional[int] = None
    responded_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Include user info
    user: Optional[dict] = None  # Will be populated with user data
    
    class Config:
        from_attributes = True


class FeedbackListResponse(BaseModel):
    """Paginated feedback list response"""
    items: list[FeedbackResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
