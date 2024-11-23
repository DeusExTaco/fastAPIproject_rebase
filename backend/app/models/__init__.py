# backend/models/__init__.py
from app.models.user_preferences_model import UserPreferences


# List all models for easy import
__all__ = [
    'User',
    'UserRole',
    'UserStatus',
    'UserAddress',
    'UserProfile',
    'ServerPerformance',
    'UserPreferences'
]