# Feedback Model
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from models.base import Base, TimestampMixin
from datetime import datetime


class Feedback(Base, TimestampMixin):
    """Model cho feedback/góp ý từ người dùng"""
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    category = Column(String(50), default="other")  # bug, feature_request, question, other
    status = Column(String(50), default="new")  # new, in_progress, resolved, closed
    
    # Admin response
    admin_response = Column(Text, nullable=True)
    responded_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    responded_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], backref="feedback_submitted")
    admin_user = relationship("User", foreign_keys=[responded_by], backref="feedback_responses")
    
    def __repr__(self):
        return f"<Feedback(id={self.id}, user_id={self.user_id}, status='{self.status}')>"
