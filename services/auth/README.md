# Сервис аутентификации

Микросервис для регистрации и аутентификации пользователей в системе аудиокниг.

## Описание

Этот микросервис реализует процессы **Registration** и **Authentication** в контексте Domain-Driven Design (DDD). Он предоставляет API для:

- Регистрации новых пользователей
- Аутентификации пользователей и получения JWT токенов
- Получения информации о текущем пользователе

## Архитектура

### DDD Концепции

- **User** - Сущность, представляющая пользователя системы
- **Registration** - Процесс создания нового пользователя
- **Authentication** - Процесс проверки учетных данных и выдачи токена
- **DTO** - Data Transfer Objects для передачи данных между слоями

### Технологии

- **FastAPI** - веб-фреймворк
- **SQLAlchemy** - ORM для работы с базой данных
- **Pydantic** - валидация данных
- **JWT** - токены аутентификации
- **bcrypt** - хеширование паролей

## Установка и запуск

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Настройте переменные окружения:
```bash
export SECRET_KEY="your-secret-key-here"
export DATABASE_URL="postgresql://user:password@localhost/audiostore"
```

3. Запустите сервис:
```bash
python main.py
```

Сервис будет доступен по адресу: http://localhost:8001

## API Эндпоинты

### POST /register
Регистрация нового пользователя.

**Request Body:**
```json
{
    "email": "user@example.com",
    "password": "securepassword123"
}
```

**Response:**
```json
{
    "id": 1,
    "email": "user@example.com",
    "created_at": "2024-01-01T12:00:00"
}
```

### POST /token
Получение JWT токена для аутентификации.

**Request Body (form-data):**
```
username: user@example.com
password: securepassword123
```

**Response:**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
}
```

### GET /users/me
Получение информации о текущем пользователе.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
    "id": 1,
    "email": "user@example.com",
    "created_at": "2024-01-01T12:00:00"
}
```

### GET /health
Проверка состояния сервиса.

**Response:**
```json
{
    "status": "healthy",
    "service": "auth"
}
```

## Безопасность

- Пароли хешируются с использованием bcrypt
- JWT токены имеют ограниченное время жизни (30 минут)
- Все эндпоинты используют HTTPS в продакшене
- Валидация email адресов
- Защита от дублирования пользователей

## Интеграция с другими сервисами

Этот микросервис может быть интегрирован с другими сервисами системы:

- **Catalog Service** - для персонализированных рекомендаций
- **Orders Service** - для привязки заказов к пользователям
- **Cart Service** - для сохранения корзины пользователя

## Мониторинг

Сервис предоставляет эндпоинт `/health` для проверки состояния и может быть интегрирован с системами мониторинга.
