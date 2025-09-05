"""
Конфигурационный файл для администраторов
"""

import secrets
import hashlib
from datetime import datetime, timedelta

# Фиксированные учетные данные администратора
ADMIN_CREDENTIALS = {
    "username": "admin",
    "password": "admin123"
}

# Словарь для хранения активных токенов (в реальном приложении используйте базу данных)
ACTIVE_TOKENS = {}

def verify_admin_credentials(username, password):
    """
    Проверяет учетные данные администратора
    
    Args:
        username (str): Имя пользователя
        password (str): Пароль
        
    Returns:
        bool: True если учетные данные верны, False в противном случае
    """
    return (username == ADMIN_CREDENTIALS["username"] and 
            password == ADMIN_CREDENTIALS["password"])

def generate_admin_token():
    """
    Генерирует простой токен для администратора
    
    Returns:
        str: Сгенерированный токен
    """
    # Создаем токен на основе текущего времени и случайных данных
    timestamp = str(int(datetime.now().timestamp()))
    random_data = secrets.token_hex(16)
    
    # Создаем хеш токена
    token_data = f"{ADMIN_CREDENTIALS['username']}:{timestamp}:{random_data}"
    token = hashlib.sha256(token_data.encode()).hexdigest()
    
    # Сохраняем токен с временной меткой
    ACTIVE_TOKENS[token] = {
        "username": ADMIN_CREDENTIALS["username"],
        "created_at": datetime.now(),
        "expires_at": datetime.now() + timedelta(hours=24)  # Токен действителен 24 часа
    }
    
    return token

def verify_admin_token(token):
    """
    Проверяет валидность токена администратора
    
    Args:
        token (str): Токен для проверки
        
    Returns:
        bool: True если токен валиден, False в противном случае
    """
    if not token or token not in ACTIVE_TOKENS:
        return False
    
    token_data = ACTIVE_TOKENS[token]
    
    # Проверяем, не истек ли токен
    if datetime.now() > token_data["expires_at"]:
        # Удаляем истекший токен
        del ACTIVE_TOKENS[token]
        return False
    
    return True

def revoke_admin_token(token):
    """
    Отзывает токен администратора
    
    Args:
        token (str): Токен для отзыва
    """
    if token in ACTIVE_TOKENS:
        del ACTIVE_TOKENS[token]

def get_admin_username_from_token(token):
    """
    Получает имя пользователя из токена
    
    Args:
        token (str): Токен
        
    Returns:
        str: Имя пользователя или None если токен невалиден
    """
    if verify_admin_token(token):
        return ACTIVE_TOKENS[token]["username"]
    return None

def cleanup_expired_tokens():
    """
    Очищает истекшие токены
    """
    current_time = datetime.now()
    expired_tokens = [
        token for token, data in ACTIVE_TOKENS.items()
        if current_time > data["expires_at"]
    ]
    
    for token in expired_tokens:
        del ACTIVE_TOKENS[token]
