# app/utils/security.py
from passlib.context import CryptContext

# Use Argon2 for hashing (modern and avoids bcrypt 72-byte issues)
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password: str) -> str:
    if not isinstance(password, str):
        password = str(password)
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not isinstance(plain_password, str):
        plain_password = str(plain_password)
    return pwd_context.verify(plain_password, hashed_password)


