"""
Сервис для управления промптами AI-системы.

Этот сервис отвечает за:
- Управление промптами для различных AI-сервисов
- Создание, обновление и получение промптов
- Инициализацию промптов по умолчанию
- RESTful API для работы с промптами
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
import sys
import os
from pydantic import BaseModel
from datetime import datetime

# Добавляем путь к модулю database
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from database.models import Base, Prompt
from database.connection import get_db, initialize_database, get_database_info

# Инициализация базы данных
initialize_database()

app = FastAPI(title="Prompts Manager Service", version="1.0.0")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене замените на конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic модели для API
class PromptCreate(BaseModel):
    name: str
    content: str
    description: Optional[str] = None
    is_active: str = "true"


class PromptUpdate(BaseModel):
    name: Optional[str] = None
    content: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[str] = None


class PromptResponse(BaseModel):
    id: int
    name: str
    content: str
    description: Optional[str]
    is_active: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


def create_default_prompts(db: Session) -> None:
    """
    Создает промпты по умолчанию, если их нет в базе данных.
    
    Args:
        db: Сессия базы данных
    """
    # Проверяем существование промптов
    existing_prompts = db.query(Prompt).all()
    existing_names = {prompt.name for prompt in existing_prompts}
    
    # Промпт для рекомендаций
    if 'recommendation_prompt' not in existing_names:
        recommendation_prompt = Prompt(
            name='recommendation_prompt',
            content='''Ты - эксперт по аудиокнигам. Проанализируй предпочтения пользователя и предложи 5 релевантных аудиокниг.

Пользователь интересуется: {user_preferences}
Доступные аудиокниги: {available_books}

Критерии рекомендации:
1. Соответствие жанровым предпочтениям
2. Популярность и рейтинг
3. Новизна контента
4. Разнообразие авторов

Формат ответа:
1. [Название] - [Автор] - [Краткое описание]
2. [Название] - [Автор] - [Краткое описание]
...

Объясни, почему именно эти книги подходят пользователю.''',
            description='Промпт для генерации рекомендаций аудиокниг на основе предпочтений пользователя',
            is_active='true'
        )
        db.add(recommendation_prompt)
    
    # Промпт для генерации описаний
    if 'description_prompt' not in existing_names:
        description_prompt = Prompt(
            name='description_prompt',
            content='''Ты - профессиональный копирайтер, специализирующийся на описании аудиокниг.

Создай привлекательное и информативное описание для аудиокниги:

Название: {title}
Автор: {author}
Жанр: {genre}
Основная тема: {theme}

Требования к описанию:
1. Длина: 150-300 слов
2. Захватывающее начало
3. Краткий пересказ сюжета без спойлеров
4. Упоминание ключевых особенностей
5. Призыв к действию

Стиль: профессиональный, но доступный
Тон: увлекательный, но не навязчивый

Создай описание, которое заинтересует потенциальных слушателей.''',
            description='Промпт для генерации описаний аудиокниг',
            is_active='true'
        )
        db.add(description_prompt)
    
    db.commit()


@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске приложения."""
    from database.connection import get_db_session
    with get_db_session() as db:
        create_default_prompts(db)


@app.get("/")
async def root():
    return {"message": "Prompts Manager Service is running"}


@app.get("/health")
async def health_check():
    """Проверка состояния сервиса и базы данных."""
    db_info = get_database_info()
    return {
        "status": "healthy",
        "service": "Prompts Manager Service",
        "version": "1.0.0",
        "database": db_info
    }


@app.get("/prompts", response_model=List[PromptResponse])
async def get_prompts(
    active_only: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    Получить список всех промптов.
    
    Args:
        active_only: Если True, возвращает только активные промпты
        db: Сессия базы данных
    
    Returns:
        Список промптов
    """
    query = db.query(Prompt)
    
    if active_only:
        query = query.filter(Prompt.is_active == 'true')
    
    prompts = query.all()
    return prompts


@app.get("/prompts/{prompt_id}", response_model=PromptResponse)
async def get_prompt(prompt_id: int, db: Session = Depends(get_db)):
    """
    Получить промпт по ID.
    
    Args:
        prompt_id: ID промпта
        db: Сессия базы данных
    
    Returns:
        Промпт
    """
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Промпт не найден")
    return prompt


@app.get("/prompts/name/{prompt_name}", response_model=PromptResponse)
async def get_prompt_by_name(prompt_name: str, db: Session = Depends(get_db)):
    """
    Получить промпт по имени.
    
    Args:
        prompt_name: Имя промпта
        db: Сессия базы данных
    
    Returns:
        Промпт
    """
    prompt = db.query(Prompt).filter(Prompt.name == prompt_name).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Промпт не найден")
    return prompt


@app.post("/prompts", response_model=PromptResponse)
async def create_prompt(prompt_data: PromptCreate, db: Session = Depends(get_db)):
    """
    Создать новый промпт.
    
    Args:
        prompt_data: Данные для создания промпта
        db: Сессия базы данных
    
    Returns:
        Созданный промпт
    """
    # Проверяем, что промпт с таким именем не существует
    existing_prompt = db.query(Prompt).filter(Prompt.name == prompt_data.name).first()
    if existing_prompt:
        raise HTTPException(status_code=400, detail="Промпт с таким именем уже существует")
    
    prompt = Prompt(
        name=prompt_data.name,
        content=prompt_data.content,
        description=prompt_data.description,
        is_active=prompt_data.is_active
    )
    
    db.add(prompt)
    db.commit()
    db.refresh(prompt)
    
    return prompt


@app.put("/prompts/{prompt_id}", response_model=PromptResponse)
async def update_prompt(
    prompt_id: int,
    prompt_data: PromptUpdate,
    db: Session = Depends(get_db)
):
    """
    Обновить промпт по ID.
    
    Args:
        prompt_id: ID промпта
        prompt_data: Данные для обновления
        db: Сессия базы данных
    
    Returns:
        Обновленный промпт
    """
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Промпт не найден")
    
    # Проверяем уникальность имени, если оно изменяется
    if prompt_data.name and prompt_data.name != prompt.name:
        existing_prompt = db.query(Prompt).filter(Prompt.name == prompt_data.name).first()
        if existing_prompt:
            raise HTTPException(status_code=400, detail="Промпт с таким именем уже существует")
    
    # Обновляем поля
    if prompt_data.name is not None:
        prompt.name = prompt_data.name
    if prompt_data.content is not None:
        prompt.content = prompt_data.content
    if prompt_data.description is not None:
        prompt.description = prompt_data.description
    if prompt_data.is_active is not None:
        prompt.is_active = prompt_data.is_active
    
    db.commit()
    db.refresh(prompt)
    
    return prompt


@app.put("/prompts/{prompt_id}/activate")
async def activate_prompt(prompt_id: int, db: Session = Depends(get_db)):
    """
    Активировать промпт.
    
    Args:
        prompt_id: ID промпта
        db: Сессия базы данных
    
    Returns:
        Сообщение об успешной активации
    """
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Промпт не найден")
    
    prompt.activate()
    db.commit()
    
    return {"message": f"Промпт '{prompt.name}' активирован"}


@app.put("/prompts/{prompt_id}/deactivate")
async def deactivate_prompt(prompt_id: int, db: Session = Depends(get_db)):
    """
    Деактивировать промпт.
    
    Args:
        prompt_id: ID промпта
        db: Сессия базы данных
    
    Returns:
        Сообщение об успешной деактивации
    """
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Промпт не найден")
    
    prompt.deactivate()
    db.commit()
    
    return {"message": f"Промпт '{prompt.name}' деактивирован"}


@app.delete("/prompts/{prompt_id}")
async def delete_prompt(prompt_id: int, db: Session = Depends(get_db)):
    """
    Удалить промпт по ID.
    
    Args:
        prompt_id: ID промпта
        db: Сессия базы данных
    
    Returns:
        Сообщение об успешном удалении
    """
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Промпт не найден")
    
    prompt_name = prompt.name
    db.delete(prompt)
    db.commit()
    
    return {"message": f"Промпт '{prompt_name}' удален"}


@app.get("/prompts/initialize/defaults")
async def initialize_default_prompts(db: Session = Depends(get_db)):
    """
    Инициализировать промпты по умолчанию.
    
    Args:
        db: Сессия базы данных
    
    Returns:
        Сообщение о результатах инициализации
    """
    try:
        create_default_prompts(db)
        return {"message": "Промпты по умолчанию успешно инициализированы"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при инициализации: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)
