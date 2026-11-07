from datetime import datetime, timedelta, timezone

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

from app import config

_hasher = PasswordHasher()

# Used when a login email doesn't exist, so the response takes the same time
DUMMY_HASH = _hasher.hash("dummy-password-for-timing")

def hash_password(password: str) -> str:
    return _hasher.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    try:
        return _hasher.verify(password_hash, password)
    except (VerificationError, InvalidHashError):
        return False

def create_access_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, config.SECRET_KEY, algorithm=config.JWT_ALGORITHM)

def decode_access_token(token: str) -> int | None:
    """Return the user id if the token is valid, otherwise None."""
    try:
        payload = jwt.decode(
            token,
            config.SECRET_KEY,
            algorithms=[config.JWT_ALGORITHM],
            options={"require": ["exp", "sub"]},
        )
        return int(payload["sub"])
    except (jwt.PyJWTError, ValueError):
        return None