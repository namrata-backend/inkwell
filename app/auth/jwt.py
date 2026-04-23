import json
import urllib.request
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwk, jwt
from jose.utils import base64url_decode

from app.config import settings

_JWKS_URL = (
    f"https://cognito-idp.{settings.AWS_REGION}.amazonaws.com/"
    f"{settings.COGNITO_USER_POOL_ID}/.well-known/jwks.json"
)

_jwks_cache: Optional[dict] = None

bearer_scheme = HTTPBearer()


def _get_jwks() -> dict:
    global _jwks_cache
    if _jwks_cache is None:
        with urllib.request.urlopen(_JWKS_URL) as response:
            _jwks_cache = json.loads(response.read().decode())
    return _jwks_cache


def _get_public_key(token: str) -> dict:
    headers = jwt.get_unverified_headers(token)
    kid = headers["kid"]
    jwks = _get_jwks()
    for key in jwks["keys"]:
        if key["kid"] == kid:
            return jwk.construct(key)
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"code": "INVALID_TOKEN", "message": "Token signing key not found"},
    )


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> str:
    token = credentials.credentials
    try:
        public_key = _get_public_key(token)
        message, encoded_sig = token.rsplit(".", 1)
        decoded_sig = base64url_decode(encoded_sig.encode())
        if not public_key.verify(message.encode(), decoded_sig):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "INVALID_TOKEN",
                    "message": "Token signature is invalid",
                },
            )
        claims = jwt.get_unverified_claims(token)
        if claims.get("iss") != (
            f"https://cognito-idp.{settings.AWS_REGION}.amazonaws.com/"
            f"{settings.COGNITO_USER_POOL_ID}"
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "INVALID_TOKEN", "message": "Token issuer is invalid"},
            )
        user_id: str = claims["sub"]
        return user_id
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_TOKEN", "message": "Token is invalid or expired"},
        )
