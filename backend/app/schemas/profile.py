# backend/app/schemas/profile.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl


class UserProfileBase(BaseModel):
    """Base schema for UserProfile with common attributes."""
    avatar_url: Optional[HttpUrl] = None
    bio: Optional[str] = Field(None, max_length=1000)
    location: Optional[str] = Field(None, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=20)


class UserProfileCreate(UserProfileBase):
    """Schema for creating a new user profile."""
    user_id: int


class UserProfileUpdate(UserProfileBase):
    """Schema for updating a user profile."""
    pass


class UserProfileInDBBase(UserProfileBase):
    """Base schema for UserProfile from DB, including common fields."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserProfile(UserProfileInDBBase):
    """Schema for returning a user profile."""
    pass