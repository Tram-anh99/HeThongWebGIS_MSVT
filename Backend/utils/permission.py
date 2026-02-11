# Permission utilities for role-based access control
from fastapi import HTTPException, status
from typing import List, Optional
from functools import wraps
from models import User


def require_role(allowed_roles: List[str]):
    """
    Decorator to check if user has one of the allowed roles
    
    Usage:
        @require_role(['admin', 'manager'])
        async def some_endpoint(current_user: User = Depends(get_current_active_user)):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: User = None, **kwargs):
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            if current_user.role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Requires one of roles: {', '.join(allowed_roles)}"
                )
            
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator


def check_province_access(user: User, province_name: str) -> bool:
    """
    Check if user has access to data from a specific province
    
    Args:
        user: Current user object
        province_name: Province name to check access for
        
    Returns:
        True if user has access, False otherwise
    """
    # Admin has access to all provinces
    if user.role == "admin":
        return True
    
    # Manager only has access to their assigned province
    if user.role == "manager":
        # Match province_code with province_name
        # This assumes province_code is a short code like "HN", "HCM"
        # and province_name might be full name like "Hà Nội"
        # For exact matching, we use province_code directly
        return user.province_code == province_name
    
    # Other roles (farmer, customs) don't have province-level access
    return False


def get_province_filter(user: User) -> Optional[str]:
    """
    Get the province filter for queries based on user role
    
    Args:
        user: Current user object
        
    Returns:
        Province code/name string if user is a manager, None otherwise
    """
    if user.role == "manager" and user.province_code:
        return user.province_code
    
    return None


def validate_province_permission(user: User, province_name: str):
    """
    Validate that user has permission to access data from a province.
    Raises HTTPException if access is denied.
    
    Args:
        user: Current user object
        province_name: Province name to validate access for
        
    Raises:
        HTTPException: If user doesn't have permission
    """
    if user.role == "manager":
        if not user.province_code:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Manager account has no province assigned"
            )
        
        if user.province_code != province_name:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. You can only access data from province: {user.province_code}"
            )


def is_manager_or_admin(user: User) -> bool:
    """
    Check if user is manager or admin
    
    Args:
        user: Current user object
        
    Returns:
        True if user is manager or admin, False otherwise
    """
    return user.role in ["admin", "manager"]
