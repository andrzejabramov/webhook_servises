import hashlib
import secrets
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": user_id, "exp": expire}
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def create_refresh_token() -> tuple[str, str]:
    """Возвращает (token, token_hash)"""
    token = secrets.token_urlsafe(64)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    return token, token_hash

def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

def normalize_login(login: str) -> str:
    """Нормализация: email → lower, phone → E.164 (упрощённо)"""
    login = login.strip()
    if "@" in login:
        return login.lower()
    # Простая нормализация телефона: оставить только цифры, добавить +
    digits = "".join(filter(str.isdigit, login))
    if digits.startswith("7"):
        return f"+{digits}"
    if digits.startswith("8"):
        return f"+7{digits[1:]}"
    return login  # fallback