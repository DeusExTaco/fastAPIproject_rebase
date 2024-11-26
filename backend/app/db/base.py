from typing import Any, Dict, Iterator
from datetime import datetime
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


# noinspection PyMethodParameters
class Base(DeclarativeBase):
    """Base class for all database models."""

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Generate tablename from class name."""
        return cls.__name__.lower()

    # Common columns for all models
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation of the model
        """
        result: Dict[str, Any] = {}
        # Iterate over column values explicitly
        for column in self.__table__.columns.values():
            result[column.name] = getattr(self, column.name)
        return result

    def __repr__(self) -> str:
        """String representation of the model."""
        # Iterate over column values explicitly
        items: Iterator[str] = (
            f"{column.name}={getattr(self, column.name)!r}"
            for column in self.__table__.columns.values()
        )
        return f"{self.__class__.__name__}({', '.join(items)})"
