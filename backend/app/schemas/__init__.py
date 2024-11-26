# backend/app/schemas/__init__.py
from .role import Role, RoleCreate, RoleUpdate
from .profile import UserProfile, UserProfileCreate, UserProfileUpdate
from .user import User, UserCreate, UserUpdate, UserWithProfile

__all__ = [
    # User schemas
    "User",
    "UserCreate",
    "UserUpdate",
    "UserWithProfile",
    # Profile schemas
    "UserProfile",
    "UserProfileCreate",
    "UserProfileUpdate",
    # Role schemas
    "Role",
    "RoleCreate",
    "RoleUpdate",
]