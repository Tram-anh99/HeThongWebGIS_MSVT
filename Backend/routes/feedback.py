# Feedback Routes
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from database import get_db
from models import User, Feedback
from schemas.feedback import FeedbackCreate, FeedbackUpdate, FeedbackResponse, FeedbackListResponse
from utils.auth import get_current_active_user
from utils.pagination import paginate

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("/", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def create_feedback(
    feedback: FeedbackCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Tạo feedback mới
    """
    new_feedback = Feedback(
        user_id=current_user.id,
        subject=feedback.subject,
        message=feedback.message,
        category=feedback.category,
        status="new"
    )
    db.add(new_feedback)
    db.commit()
    db.refresh(new_feedback)
    
    return new_feedback


@router.get("/", response_model=FeedbackListResponse)
async def get_my_feedback(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    category: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Lấy danh sách feedback của user hiện tại
    """
    query = db.query(Feedback).filter(Feedback.user_id == current_user.id)
    
    if status:
        query = query.filter(Feedback.status == status)
    if category:
        query = query.filter(Feedback.category == category)
        
    query = query.order_by(Feedback.created_at.desc())
    
    return paginate(query, page, page_size)


@router.get("/all", response_model=FeedbackListResponse)
async def get_all_feedback(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    category: Optional[str] = None,
    user_id: Optional[int] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Lấy tất cả feedback (Admin only)
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    query = db.query(Feedback)
    
    if status:
        query = query.filter(Feedback.status == status)
    if category:
        query = query.filter(Feedback.category == category)
    if user_id:
        query = query.filter(Feedback.user_id == user_id)
        
    query = query.order_by(Feedback.created_at.desc())
    
    result = paginate(query, page, page_size)
    
    # Add user info to each feedback
    for item in result['items']:
        user = db.query(User).filter(User.id == item.user_id).first()
        if user:
            item.user = {
                'id': user.id,
                'username': user.username,
                'full_name': user.full_name,
                'role': user.role
            }
    
    return result


@router.get("/{feedback_id}", response_model=FeedbackResponse)
async def get_feedback(
    feedback_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Lấy chi tiết feedback
    """
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    # Check permission: user can only see their own feedback, admin can see all
    if feedback.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this feedback"
        )
    
    return feedback


@router.put("/{feedback_id}", response_model=FeedbackResponse)
async def update_feedback(
    feedback_id: int,
    feedback_update: FeedbackUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Cập nhật feedback
    - User: có thể sửa subject/message nếu chưa được admin trả lời
    - Admin: có thể update status và admin_response
    """
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    # Check permission
    is_owner = feedback.user_id == current_user.id
    is_admin = current_user.role == "admin"
    
    if not is_owner and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this feedback"
        )
    
    # User can only update their own feedback if not yet responded
    if is_owner and not is_admin:
        if feedback.admin_response:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot edit feedback that has been responded to"
            )
        if feedback_update.subject:
            feedback.subject = feedback_update.subject
        if feedback_update.message:
            feedback.message = feedback_update.message
        if feedback_update.category:
            feedback.category = feedback_update.category
    
    # Admin can update status and response
    if is_admin:
        if feedback_update.status:
            feedback.status = feedback_update.status
        if feedback_update.admin_response:
            feedback.admin_response = feedback_update.admin_response
            feedback.responded_by = current_user.id
            feedback.responded_at = datetime.utcnow()
    
    db.commit()
    db.refresh(feedback)
    
    return feedback


@router.delete("/{feedback_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_feedback(
    feedback_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Xóa feedback
    - User: có thể xóa feedback của mình nếu chưa được admin trả lời
    - Admin: có thể xóa bất kỳ feedback nào
    """
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    is_owner = feedback.user_id == current_user.id
    is_admin = current_user.role == "admin"
    
    if not is_owner and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this feedback"
        )
    
    # User can only delete if not yet responded
    if is_owner and not is_admin and feedback.admin_response:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete feedback that has been responded to"
        )
    
    db.delete(feedback)
    db.commit()
    
    return None


@router.get("/stats/counts")
async def get_feedback_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Lấy thống kê số lượng feedback (Admin only)
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    total = db.query(Feedback).count()
    new_count = db.query(Feedback).filter(Feedback.status == "new").count()
    in_progress = db.query(Feedback).filter(Feedback.status == "in_progress").count()
    resolved = db.query(Feedback).filter(Feedback.status == "resolved").count()
    
    return {
        "total": total,
        "new": new_count,
        "in_progress": in_progress,
        "resolved": resolved
    }
