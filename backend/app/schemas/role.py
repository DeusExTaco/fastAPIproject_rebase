# backend/app/schemas/role.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class RoleBase(BaseModel):
    """Base schema for Role with common attributes."""
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=200)


class RoleCreate(RoleBase):
    """Schema for creating a new role."""
    pass


class RoleUpdate(RoleBase):
    """Schema for updating a role."""
    name: Optional[str] = Field(None, min_length=1, max_length=50)


class RoleInDBBase(RoleBase):
    """Base schema for Role from DB, including common fields."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Role(RoleInDBBase):
    """Schema for returning a role."""
    pass