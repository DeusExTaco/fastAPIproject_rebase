# auth/auth0_middleware.py
from functools import lru_cache
from typing import List
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import requests
from jwt.algorithms import RSAAlgorithm
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from config import get_settings

settings = get_settings()
security = HTTPBearer()


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
        except Exception as e:
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
            credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> dict:
        """Verify the JWT token and return the decoded payload"""
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
                detail="Token has expired"
            )
        except InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid claims (audience or issuer)"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Unable to verify token: {str(e)}"
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


# Helper function to get current user from token
async def get_current_user(
        payload: dict = Depends(get_auth0_middleware().verify_token)
) -> dict:
    return {
        "sub": payload.get("sub"),
        "email": payload.get("email"),
        "roles": payload.get("permissions", [])
    }