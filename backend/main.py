# backend/main.py

import logging
from typing import Optional, Dict, Any

from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from config import get_settings
from starlette.middleware.base import BaseHTTPMiddleware
from app.middleware.cors_middleware import setup_cors
from app.api.v1.routes.user_routes import router as user_router
from app.api.v1.routes.user_profile_routes import router as profile_router
from app.api.v1.routes.user_preferences_routes import router as preferences_router
from app.api.v1.routes.auth_routes import router as auth_router

ua = "uvicorn.access"

# Get settings instance
settings = get_settings()

# Base logging configuration
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format=settings.LOG_FORMAT,
    force=True
)

# Configure uvicorn access logs
logging.getLogger(ua).handlers = []
logging.getLogger(ua).propagate = True
logging.getLogger(ua).setLevel(logging.INFO)

# Get root logger
root_logger = logging.getLogger()
root_logger.setLevel(getattr(logging, settings.LOG_LEVEL))

# Application logger
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.API_VERSION
)


# Custom error handling middleware
class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Any) -> Any:
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(f"Unhandled error: {str(e)}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "An internal server error occurred",
                    "message": str(e) if settings.DEBUG else None
                }
            )

# Configure CORS
setup_cors(app)

# Add middleware in correct order - order is important!
# 1. Error handling should be first to catch all errors
# noinspection PyTypeChecker
app.add_middleware(ErrorHandlingMiddleware)


# Include auth routes
app.include_router(
    auth_router,
    prefix="/api/auth",
    tags=["Authentication"]
)

app.include_router(
    user_router,
    prefix="/api/users",
    tags=["User Management"]
)

app.include_router(
    profile_router,
    prefix="/api",
    tags=["User Profile"]
)

app.include_router(
    preferences_router,
    prefix="/api",
    tags=["User Preferences"]
)

# Public Health Check Endpoint
@app.get("/api/health", tags=["Health"])
async def health_check():

    return {
        "status": "healthy",
        "version": settings.API_VERSION,
        "debug_mode": settings.DEBUG,
        "environment": settings.ENVIRONMENT,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )