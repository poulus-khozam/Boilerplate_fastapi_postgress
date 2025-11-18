# src/core/security.py
from datetime import datetime, timedelta
from typing import Any, Union

from jose import jwt
from passlib.context import CryptContext

from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(
    subject: Union[str, Any],
    expires_delta: timedelta = None,
    additional_claims: dict = None
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    # Start with the standard claims
    to_encode = {"exp": expire, "sub": str(subject)}

    # Add any extra claims if they exist
    if additional_claims:
        to_encode.update(additional_claims)

    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    password_bytes = password.encode('utf-8')
    # Truncate the byte string to 72 bytes.
    truncated_bytes = password_bytes[:72]
    # Decode it back to a string for passlib. Use 'ignore' to prevent errors
    # if a multi-byte character was cut in the middle.
    password_to_hash = truncated_bytes.decode('utf-8', 'ignore')
    return pwd_context.hash(password_to_hash)
