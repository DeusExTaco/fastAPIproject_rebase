# main_new_BKP.py
import logging
from typing import Dict, Optional

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
import jwt
import requests
from jwt.algorithms import RSAAlgorithm
from functools import lru_cache
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

ua = "uvicorn.access"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings"""
    AUTH0_DOMAIN: str
    AUTH0_AUDIENCE: str
    AUTH0_CLIENT_ID: str
    AUTH0_CLIENT_SECRET: str
    CORS_ORIGINS: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        case_sensitive=True
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
security = HTTPBearer()


class Auth0Validator:
    """Auth0 token validation handler"""

    def __init__(self):
        self.domain = settings.AUTH0_DOMAIN
        self.audience = settings.AUTH0_AUDIENCE
        self.jwks = None
        self.jwks_url = f"https://{self.domain}/.well-known/jwks.json"
        self.algorithms = ["RS256"]
        self._load_jwks()

    def _load_jwks(self) -> None:
        """Load JSON Web Key Set from Auth0"""
        try:
            response = requests.get(self.jwks_url)
            response.raise_for_status()
            self.jwks = response.json()
            logger.info("Successfully loaded JWKS")
        except Exception as e:
            logger.error(f"Failed to load JWKS: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to load JWKS: {str(e)}"
            )

    def _get_signing_key(self, kid: str) -> str:
        """Get signing key from JWKS"""
        if not self.jwks:
            self._load_jwks()

        for key in self.jwks.get("keys", []):
            if key.get("kid") == kid:
                return RSAAlgorithm.from_jwk(key)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to find appropriate key"
        )

    async def verify_token(
            self,
            auth_credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> dict:
        """Verify the JWT token and return the decoded payload"""
        token = auth_credentials.credentials
        try:
            unverified_header = jwt.get_unverified_header(token)
            key = self._get_signing_key(unverified_header.get("kid"))

            payload = jwt.decode(
                token,
                key,
                algorithms=self.algorithms,
                audience=self.audience,
                issuer=f"https://{self.domain}/"
            )

            logger.info(f"Token verified for user: {payload.get('sub')}")
            return payload

        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}"
            )


# Initialize FastAPI app
app = FastAPI(
    title="FastAPI Auth0 Demo",
    description="A minimal FastAPI application with Auth0 authentication",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Auth0 validator
auth0_validator = Auth0Validator()


class HealthResponse(BaseModel):
    status: str
    auth0: Dict[str, str]
    error: Optional[str] = None


@app.get("/api/public")
async def public_route():
    """Public endpoint that doesn't require authentication"""
    return {
        "message": "This is a public endpoint",
        "status": "success"
    }


@app.get("/api/private")
async def private_route(payload: Dict = Depends(auth0_validator.verify_token)):
    """Private endpoint that requires authentication"""
    return {
        "message": "This is a private endpoint",
        "user": payload.get("sub"),
        "status": "success"
    }


@app.get("/api/user-profile")
async def get_user_profile(payload: Dict = Depends(auth0_validator.verify_token)):
    """Get the current user's profile information"""
    return {
        "sub": payload.get("sub"),
        "email": payload.get("email"),
        "permissions": payload.get("permissions", []),
        "metadata": {
            "nickname": payload.get("nickname"),
            "name": payload.get("name"),
            "picture": payload.get("picture"),
            "updated_at": payload.get("updated_at"),
            "email_verified": payload.get("email_verified", False),
        }
    }


@app.get("/api/verify")
async def verify_token_endpoint(payload: Dict = Depends(auth0_validator.verify_token)):
    """Verify a token and return its payload"""
    return {
        "message": "Token is valid",
        "payload": payload
    }


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Test JWKS fetch to verify Auth0 connectivity
        requests.get(f"https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json").raise_for_status()
        return HealthResponse(
            status="healthy",
            auth0={
                "domain": settings.AUTH0_DOMAIN,
                "audience": settings.AUTH0_AUDIENCE,
            }
        )
    except Exception as e:
        return HealthResponse(
            status="unhealthy",
            auth0={
                "domain": settings.AUTH0_DOMAIN,
                "audience": settings.AUTH0_AUDIENCE,
            },
            error=str(e)
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )