# backend/app/models/profile.py
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import TimeStampedModel

if TYPE_CHECKING:
    from .user import User  # Import only for type checking


class UserProfile(TimeStampedModel):
    """Extended user profile information."""

    # Override the default table name
    __tablename__ = "user_profile"

    # Foreign key to user
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)

    # Profile fields
    avatar_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    phone_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Relationship back to user - using string literal for type hint
    user: Mapped["User"] = relationship("User", back_populates="profile")