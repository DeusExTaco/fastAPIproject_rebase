# backend/app/models/role.py
from enum import Enum as PyEnum
from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column
from .base import TimeStampedModel

class RoleType(str, PyEnum):
    ADMIN = "ADMIN"
    MODERATOR = "MODERATOR"
    USER = "USER"

class Role(TimeStampedModel):
    """Role model for storing user roles."""
    name: Mapped[RoleType] = mapped_column(
        Enum(RoleType),
        unique=True,
        nullable=False
    )
    description: Mapped[str] = mapped_column(String(200))