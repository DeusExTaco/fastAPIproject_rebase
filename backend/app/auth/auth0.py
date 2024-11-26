# auth/auth0.py
from functools import lru_cache, wraps
from typing import Dict, List, Optional, Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
import requests
from jwt.algorithms import RSAAlgorithm

from ..config import get_settings

settings = get_settings()

# Auth0 configuration
AUTH0_DOMAIN = settings.AUTH0_DOMAIN
AUTH0_AUDIENCE = settings.AUTH0_AUDIENCE
ALGORITHMS = ["RS256"]

# HTTP bearer token scheme
security = HTTPBearer()


class Auth0Handler:
    def __init__(self):
        self.jwks = None
        self.jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
        self._load_jwks()

    def _load_jwks(self) -> None:
        """Load JSON Web Key Set from Auth0"""
        try:
            jwks_response = requests.get(self.jwks_url)
            jwks_response.raise_for_status()
            self.jwks = jwks_response.json()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
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

    def verify_token(self, token: str) -> Dict:
        try:
            unverified_headers = jwt.get_unverified_header(token)
            kid = unverified_headers.get("kid")
            if not kid:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="No key ID in token header"
                )

            signing_key = self._get_signing_key(kid)

            payload = jwt.decode(
                token,
                signing_key,
                algorithms=ALGORITHMS,
                audience=AUTH0_AUDIENCE,
                issuer=f"https://{AUTH0_DOMAIN}/"
            )

            return payload

        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token claims: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Unable to verify token: {str(e)}"
            )


@lru_cache()
def get_auth0_handler() -> Auth0Handler:
    return Auth0Handler()


async def verify_token(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        auth0_handler: Auth0Handler = Depends(get_auth0_handler)
) -> Dict:
    token = credentials.credentials
    return auth0_handler.verify_token(token)


def has_role(required_roles: List[str]):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            token = await verify_token(
                credentials=Depends(security),
                auth0_handler=Depends(get_auth0_handler)
            )

            # Get roles from token payload
            user_roles = token.get("https://your-namespace/roles", [])

            # Check if user has any of the required roles
            if not any(role in user_roles for role in required_roles):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


# Example protected route decorator
def protected_route(roles: Optional[List[str]] = None):
    """Decorator for routes that require authentication and optional role-based access"""
    dependencies = [Depends(verify_token)]
    if roles:
        dependencies.append(Depends(has_role(roles)))
    return dependencies