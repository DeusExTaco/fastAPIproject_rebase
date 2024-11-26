# backend/app/models/user.py
from typing import Optional, List
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import TimeStampedModel
from .role import Role
from .profile import UserProfile  # Add import for UserProfile

# Association table for user-role many-to-many relationship
user_roles = Table(
    'user_roles',
    TimeStampedModel.metadata,
    Column('user_id', ForeignKey('user.id'), primary_key=True),
    Column('role_id', ForeignKey('role.id'), primary_key=True)
)


class User(TimeStampedModel):
    """User model for storing user account information."""

    # Basic user information
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)

    # Auth fields
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    auth0_id: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)

    # Timestamps
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    email_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    roles: Mapped[List[Role]] = relationship(
        secondary=user_roles,
        lazy="select",
        cascade="all, delete"
    )
    profile: Mapped[UserProfile] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )