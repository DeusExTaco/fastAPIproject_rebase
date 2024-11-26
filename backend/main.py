# backend/main.py
import logging
from typing import Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.config import get_settings
from starlette.middleware.base import BaseHTTPMiddleware
from app.middleware.cors_middleware import setup_cors
from app.api.v1.routes.user_routes import router as user_router
from app.api.v1.routes.profile_routes import router as profile_router
from app.api.v1.routes.auth_routes import router as auth_router
from app.db.init_db import init_db


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


@asynccontextmanager
async def lifespan(_: FastAPI):
    """
    Lifespan context manager for the FastAPI application.
    Handles startup and shutdown events.
    """
    # Startup
    try:
        logger.info("Starting up application...")
        logger.info("Initializing database...")
        init_db()
        logger.info("Database initialization completed successfully")
        yield
    except Exception as e:
        logger.error(f"Startup failed: {str(e)}")
        if not settings.DEBUG:
            logger.critical("Application startup failed in production - shutting down")
            raise
        yield
    finally:
        # Shutdown
        logger.info("Shutting down application...")


# Initialize FastAPI with lifespan
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.API_VERSION,
    lifespan=lifespan
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


app.include_router(
    auth_router,
    prefix="/api/auth",
    tags=["Authentication"]
)

app.include_router(
    user_router,
    prefix="/api/user",
    tags=["User Management"]
)

app.include_router(
    profile_router,
    prefix="/api",
    tags=["User Profile"]
)


# Public Health Check Endpoint
@app.get("/api/health", tags=["Health"])
async def health_check():
    """Health check endpoint to verify service status"""
    try:
        return {
            "status": "healthy",
            "version": settings.API_VERSION,
            "debug_mode": settings.DEBUG,
            "environment": settings.ENVIRONMENT,
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "version": settings.API_VERSION,
                "debug_mode": settings.DEBUG,
                "environment": settings.ENVIRONMENT,
                "error": str(e) if settings.DEBUG else "Service unavailable"
            }
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )