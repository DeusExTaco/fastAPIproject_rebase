# app/api/v1/routes/auth_routes.py
from fastapi import APIRouter, HTTPException, status, Response, Request, Depends
import requests
import logging
from jwt import decode, get_unverified_header
from jwt.exceptions import PyJWTError
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
import base64
from typing import Union
from ....config import get_settings

router = APIRouter()
settings = get_settings()
logger = logging.getLogger(__name__)


def ensure_bytes(key: Union[str, bytes]) -> bytes:
    """Convert string to bytes if needed."""
    if isinstance(key, str):
        return key.encode('utf-8')
    return key


def decode_value(val: str) -> int:
    """Decode JWT base64 value to integer."""
    # Ensure proper padding
    padded = val + '=' * (4 - len(val) % 4)
    # Convert to bytes first
    decoded = base64.urlsafe_b64decode(ensure_bytes(padded))
    return int.from_bytes(decoded, 'big')


def get_public_key(jwk: dict) -> bytes:
    """Convert JWK to PEM format."""
    e = decode_value(jwk['e'])
    n = decode_value(jwk['n'])

    numbers = RSAPublicNumbers(e=e, n=n)
    key = numbers.public_key(backend=default_backend())

    return key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

def fetch_user_info(access_token: str):
    userinfo_url = f"https://{settings.AUTH0_DOMAIN}/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(userinfo_url, headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch user info")
    return response.json()

async def get_current_user(request: Request):
    """
    Get the current user from the access token in cookies
    """
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    try:
        # Get JWKS
        jwks_url = f"https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json"
        jwks_response = requests.get(jwks_url)
        jwks = jwks_response.json()

        # Decode header to get key ID
        header = get_unverified_header(access_token)
        rsa_key = None

        # Find the matching key in JWKS
        for key in jwks["keys"]:
            if key["kid"] == header["kid"]:
                rsa_key = get_public_key(key)
                break

        if not rsa_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token key"
            )

        # Verify and decode token
        payload = decode(
            access_token,
            key=rsa_key,
            algorithms=["RS256"],
            audience=settings.AUTH0_AUDIENCE,
            issuer=f"https://{settings.AUTH0_DOMAIN}/"
        )

        user_info = fetch_user_info(access_token)
        payload.update(user_info)
        return payload

    except PyJWTError as e:
        logger.error(f"Token validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    except Exception as e:
        logger.error(f"Unexpected error during token validation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication error"
        )


@router.get("/me")
async def get_user_profile(user: dict = Depends(get_current_user)):
    """
    Get current user profile information
    """
    try:
        return {
            "sub": user.get("sub"),
            "email": user.get("email"),
            "name": user.get("name", user.get("email")),
            "picture": user.get("picture"),
            "email_verified": user.get("email_verified", False),
            "roles": user.get("permissions", []),
            "updated_at": user.get("updated_at"),
        }
    except Exception as e:
        logger.error(f"Error processing user profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing user profile"
        )


# noinspection PyUnusedLocal
@router.get("/callback")
async def auth_callback(
        response: Response,
        code: str,
        state: str | None = None,
):
    """
    Auth0 callback endpoint that exchanges the authorization code for tokens
    """
    logger.info(f"Received authorization code: {code}")
    try:
        token_url = f"https://{settings.AUTH0_DOMAIN}/oauth/token"
        callback_url = f"{settings.APP_URL}/api/auth/callback"

        token_payload = {
            "grant_type": "authorization_code",
            "client_id": settings.AUTH0_CLIENT_ID,
            "client_secret": settings.AUTH0_CLIENT_SECRET,
            "code": code,
            "redirect_uri": callback_url
        }

        # Exchange the authorization code for tokens
        token_response = requests.post(token_url, json=token_payload)

        if not token_response.ok:
            error_details = token_response.json()
            logger.error(f"Token exchange failed. Status: {token_response.status_code}")
            logger.error(f"Response body: {error_details}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Token exchange failed: {error_details.get('error_description', '')}"
            )

        logger.info(f"Token exchange succeeded: {token_response.json()}")
        tokens = token_response.json()
        logger.info("Token exchange successful")

        # Set secure cookies
        response.set_cookie(
            "access_token",
            tokens["access_token"],
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=3600  # 1 hour
        )

        if "refresh_token" in tokens:
            response.set_cookie(
                "refresh_token",
                tokens["refresh_token"],
                httponly=True,
                secure=True,
                samesite="lax",
                max_age=2592000  # 30 days
            )

        # Redirect to landing page instead of frontend root
        response.status_code = status.HTTP_307_TEMPORARY_REDIRECT
        response.headers["Location"] = f"{settings.FRONTEND_URL}/landing"

        return {
            "status": "success"
        }

    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed during token exchange: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to exchange authorization code: {str(e)}"
        )


@router.post("/refresh")
async def refresh_token_endpoint(request: Request, response: Response):
    """
    Refresh the access token using the refresh token
    """
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No refresh token available"
        )

    try:
        token_url = f"https://{settings.AUTH0_DOMAIN}/oauth/token"
        refresh_payload = {
            "grant_type": "refresh_token",
            "client_id": settings.AUTH0_CLIENT_ID,
            "client_secret": settings.AUTH0_CLIENT_SECRET,
            "refresh_token": refresh_token
        }

        token_response = requests.post(token_url, json=refresh_payload)
        token_response.raise_for_status()
        new_tokens = token_response.json()

        # Set new access token cookie
        response.set_cookie(
            "access_token",
            new_tokens["access_token"],
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=3600
        )

        return {"status": "success"}

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to refresh token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to refresh token: {str(e)}"
        )


@router.post("/logout")
async def logout(response: Response):
    """
    Clear auth cookies and redirect to Auth0 logout
    """
    # Clear all auth-related cookies with proper flags
    response.delete_cookie(
        "access_token",
        httponly=True,
        secure=True,
        samesite="lax",
        path="/"  # Important: ensure cookie is deleted for all paths
    )
    response.delete_cookie(
        "refresh_token",
        httponly=True,
        secure=True,
        samesite="lax",
        path="/"
    )

    # Construct Auth0 logout URL
    logout_url = (
        f"https://{settings.AUTH0_DOMAIN}/v2/logout?"
        f"client_id={settings.AUTH0_CLIENT_ID}&"
        f"returnTo={settings.FRONTEND_URL}"
    )

    logger.info("User logged out successfully")
    return {
        "status": "success",
        "logout_url": logout_url
    }