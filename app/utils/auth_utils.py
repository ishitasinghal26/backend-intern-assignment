from datetime import datetime, timedelta
import jwt
from ..config import settings

def create_access_token(data: dict, expires_minutes: int = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=expires_minutes or settings.JWT_EXP_MINUTES
    )
    to_encode.update({"exp": expire})
    encoded = jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded

def decode_token(token: str) -> dict:
    return jwt.decode(
        token,
        settings.JWT_SECRET,
        algorithms=[settings.JWT_ALGORITHM],
    )
