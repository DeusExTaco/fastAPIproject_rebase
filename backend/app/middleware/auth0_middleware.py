# backend/app/middleware/auth0_middleware.py
from functools import lru_cache
from typing import List, Optional, Dict
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
import requests
from jwt.algorithms import RSAAlgorithm

from ..config import get_settings

settings = get_settings()

na = "Not authenticated"

class CustomHTTPBearer(HTTPBearer):
    async def __call__(
            self, request: Request
    ) -> Optional[HTTPAuthorizationCredentials]:
        try:
            return await super().__call__(request)
        except HTTPException as e:
            if e.status_code == 403:
                # Convert 403 to 401 for missing or invalid bearer tokens
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=na,
                    headers={"WWW-Authenticate": "Bearer"},
                )
            raise e


security = CustomHTTPBearer(auto_error=True)


class Auth0Middleware:
    def __init__(self):
        self.domain = settings.AUTH0_DOMAIN
        self.audience = settings.AUTH0_AUDIENCE
        self.algorithms = ["RS256"]
        self.jwks = None
        self.jwks_url = f"https://{self.domain}/.well-known/jwks.json"
        self._load_jwks()

    def _load_jwks(self) -> None:
        """Load JSON Web Key Set from Auth0"""
        try:
            response = requests.get(self.jwks_url)
            response.raise_for_status()
            self.jwks = response.json()
        except requests.RequestException as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Authentication service unavailable: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
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
            detail="Invalid token signature",
            headers={"WWW-Authenticate": "Bearer"},
        )

    async def verify_token(
            self,
            credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
    ) -> Dict:
        """Verify the JWT token and return the decoded payload"""
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=na,
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            token = credentials.credentials
            unverified_header = jwt.get_unverified_header(token)
            key = self._get_signing_key(unverified_header.get("kid"))

            payload = jwt.decode(
                token,
                key,
                algorithms=self.algorithms,
                audience=self.audience,
                issuer=f"https://{self.domain}/"
            )

            return payload

        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Authentication failed: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )

    @staticmethod
    def verify_permissions(payload: dict, required_roles: List[str]) -> bool:
        """Verify if the user has any of the required roles"""
        token_roles = payload.get("permissions", [])
        return any(role in token_roles for role in required_roles)

    def require_roles(self, required_roles: List[str]):
        """Decorator to verify user roles"""

        async def role_verifier(
                payload: dict = Depends(self.verify_token)
        ):
            if not self.verify_permissions(payload, required_roles):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
            return payload

        return role_verifier


@lru_cache()
def get_auth0_middleware() -> Auth0Middleware:
    return Auth0Middleware()


async def get_current_user(
        payload: dict = Depends(get_auth0_middleware().verify_token)
) -> dict:
    """Get current user from token payload"""
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=na,
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "sub": payload.get("sub"),
        "email": payload.get("email"),
        "roles": payload.get("permissions", [])
    }


def protected_route(roles: Optional[List[str]] = None):
    """Helper function for protected routes"""
    auth0 = get_auth0_middleware()
    dependencies = [Depends(auth0.verify_token)]
    if roles:
        dependencies.append(Depends(auth0.require_roles(roles)))
    return dependencies