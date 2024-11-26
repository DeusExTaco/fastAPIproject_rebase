# backend/app/schemas/user.py
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from pydantic import BaseModel, EmailStr, Field

from .role import Role

# Handle circular imports
if TYPE_CHECKING:
    from .profile import UserProfile


class UserBase(BaseModel):
    """Base schema for User with common attributes."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    is_active: bool = True


class UserCreate(UserBase):
    """Schema for creating a new user."""
    auth0_id: str = Field(..., max_length=128)


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None


class UserInDBBase(UserBase):
    """Base schema for User from DB, including common fields."""
    id: int
    auth0_id: str
    is_verified: bool
    email_verified_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    roles: List[Role]

    class Config:
        from_attributes = True


class User(UserInDBBase):
    """Schema for returning a user."""
    pass


class UserWithProfile(User):
    """Schema for returning a user with profile information."""
    from .profile import UserProfile  # Import here to avoid circular import
    profile: Optional[UserProfile] = None

    class Config:
        from_attributes = True