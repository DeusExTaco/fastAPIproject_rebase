# app/api/v1/routes/profile_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict

from ....middleware.auth0_middleware import get_current_user  # Adjusted import
from ....auth.auth0 import protected_route  # Adjusted import

router = APIRouter()

@router.get("/profiles/{user_id}", dependencies=protected_route())
async def get_profile(
    user_id: str,
    current_user: Dict = Depends(get_current_user)
) -> Dict:
    """
    Get user profile
    """
    if current_user["sub"] != user_id and "admin" not in current_user["roles"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this profile"
        )
    return {}  # TODO: Implement profile retrieval logic

@router.put("/profiles/{user_id}", dependencies=protected_route())
async def update_profile(
    user_id: str,
    current_user: Dict = Depends(get_current_user)
) -> Dict:
    """
    Update user profile
    """
    if current_user["sub"] != user_id and "admin" not in current_user["roles"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this profile"
        )
    return {"message": "Profile updated successfully"}