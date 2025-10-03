from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
# from passlib.context import CryptContext # Временно отключаем passlib/bcrypt
import os
import hashlib # Используем стандартный hashlib

# Настройки безопасности
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Контекст для хеширования паролей
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") # Временно отключаем

# --- Временное решение для диагностики ---

def get_password_hash(password: str) -> str:
    """
    Создает хеш пароля (SHA256) для диагностики.
    НЕ ИСПОЛЬЗОВАТЬ В ПРОДАКШЕНЕ БЕЗ СОЛИ!
    """
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет соответствие пароля его хешу (SHA256).
    """
    return get_password_hash(plain_password) == hashed_password

# --- Конец временного решения ---

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Создает JWT токен доступа.
    
    Args:
        data: Данные для включения в токен
        expires_delta: Время жизни токена
        
    Returns:
        JWT токен
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """
    Проверяет и декодирует JWT токен.
    
    Args:
        token: JWT токен для проверки
        
    Returns:
        Декодированные данные токена или None, если токен недействителен
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
