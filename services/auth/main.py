from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional
import sys
import os

# Добавляем путь к корневой директории проекта для импорта моделей
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from database.models import User, Base
from database.database import get_db, engine
from security import get_password_hash, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

# Создаем таблицы в базе данных
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Сервис аутентификации",
    description="Микросервис для регистрации и аутентификации пользователей",
    version="1.0.0"
)

# Настройка CORS для разрешения запросов с фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Схема OAuth2 для получения токена
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class UserCreate(BaseModel):
    """
    Схема для создания пользователя (процесс Registration).
    
    В контексте DDD это является DTO (Data Transfer Object) для
    передачи данных при регистрации пользователя.
    """
    email: EmailStr
    password: str
    
    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securepassword123"
            }
        }


class Token(BaseModel):
    """
    Схема для JWT токена доступа.
    
    В контексте DDD это является DTO для передачи токена
    аутентификации между сервисами.
    """
    access_token: str
    token_type: str = "bearer"
    
    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }


class UserResponse(BaseModel):
    """
    Схема для ответа с информацией о пользователе.
    
    В контексте DDD это является DTO для передачи данных
    пользователя без конфиденциальной информации.
    """
    id: int
    email: str
    created_at: str
    
    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm(cls, obj):
        """Преобразует объект ORM в DTO"""
        return cls(
            id=obj.id,
            email=obj.email,
            created_at=obj.created_at.isoformat() if obj.created_at else None
        )


@app.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Эндпоинт для регистрации нового пользователя.
    
    В контексте DDD это является частью процесса Registration,
    который создает новую сущность User в системе.
    
    Args:
        user_data: Данные для создания пользователя
        db: Сессия базы данных
        
    Returns:
        Созданный пользователь
        
    Raises:
        HTTPException: Если пользователь с таким email уже существует
    """
    # Проверяем, существует ли пользователь с таким email
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже зарегистрирован"
        )
    
    # Создаем нового пользователя
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return UserResponse.from_orm(new_user)


@app.post("/token", response_model=Token)
async def authenticate_for_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Эндпоинт для аутентификации и получения токена доступа.
    
    В контексте DDD это является частью процесса Authentication,
    который проверяет учетные данные пользователя и выдает токен.
    
    Args:
        form_data: Форма с учетными данными (email и password)
        db: Сессия базы данных
        
    Returns:
        JWT токен доступа
        
    Raises:
        HTTPException: Если учетные данные неверны
    """
    # Ищем пользователя по email
    user = db.query(User).filter(User.email == form_data.username).first()
    
    # Проверяем пароль
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Создаем токен доступа
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=UserResponse)
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Эндпоинт для получения информации о текущем пользователе.
    
    В контексте DDD это является частью процесса получения
    информации о пользователе по токену аутентификации.
    
    Args:
        token: JWT токен доступа
        db: Сессия базы данных
        
    Returns:
        Информация о текущем пользователе
        
    Raises:
        HTTPException: Если токен недействителен или пользователь не найден
    """
    from security import verify_token
    
    # Проверяем токен
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    email: str = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Получаем пользователя из базы данных
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return UserResponse.from_orm(user)


@app.get("/health")
async def health_check():
    """
    Эндпоинт для проверки состояния сервиса.
    
    Returns:
        Статус сервиса
    """
    return {"status": "healthy", "service": "auth"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
