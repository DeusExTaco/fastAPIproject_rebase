# app/api/v1/routes/user_routes.py
from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException, status

from ....middleware.auth0_middleware import get_current_user, get_auth0_middleware
from ....auth.auth0 import has_role

router = APIRouter()
auth0 = get_auth0_middleware()

@router.get("/")
@has_role(["admin"])  # Use as a decorator instead of dependencies parameter
async def get_users() -> List[Dict]:
    """
    Get all user (admin only)
    """
    return []  # TODO: Implement user retrieval logic

@router.get("/{user_id}")
async def get_user(
    user_id: str,
    current_user: Dict = Depends(get_current_user)
) -> Dict:
    """
    Get user by ID
    """
    if current_user["sub"] != user_id and "admin" not in current_user["roles"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's data"
        )
    return {}  # TODO: Implement user retrieval logic

@router.put("/{user_id}")
async def update_user(
    user_id: str,
    current_user: Dict = Depends(get_current_user)
) -> Dict:
    """
    Update user information
    """
    if current_user["sub"] != user_id and "admin" not in current_user["roles"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this user's data"
        )
    return {"message": "User updated successfully"}

@router.delete("/{user_id}")
@has_role(["admin"])  # Use as a decorator instead of dependencies parameter
async def delete_user(user_id: str) -> Dict:
    """
    Delete user (admin only)
    """
    return {"message": "User deleted successfully"}