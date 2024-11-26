# backend/app/db/init_db.py
import logging
from . import Base
from .session import engine, SessionLocal
from ..models import Role, RoleType

logger = logging.getLogger(__name__)


def init_db() -> None:
    """Initialize the database, creating all tables and default data."""
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Successfully created database tables.")

        # Initialize default roles
        _init_default_roles()
        logger.info("Successfully initialized default data.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise


def _init_default_roles() -> None:
    """Initialize default roles if they don't exist."""
    db = SessionLocal()
    try:
        # Check if roles already exist
        existing_roles = db.query(Role).count()
        if existing_roles == 0:
            # Create default roles
            default_roles = [
                Role(
                    name=RoleType.ADMIN,
                    description="Administrator with full access"
                ),
                Role(
                    name=RoleType.MODERATOR,
                    description="Moderator with limited administrative access"
                ),
                Role(
                    name=RoleType.USER,
                    description="Regular user with standard access"
                )
            ]
            db.add_all(default_roles)
            db.commit()
            logger.info("Created default roles")
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create default roles: {str(e)}")
        raise
    finally:
        db.close()