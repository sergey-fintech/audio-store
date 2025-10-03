"""
AI Recommender Service - Ограниченный Контекст для Core Domain AI-рекомендаций

Этот микросервис является Core Domain для системы рекомендаций аудиокниг.
Он использует LLM для анализа каталога и генерации персонализированных рекомендаций.
"""

import os
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import asyncio
import openai
from dotenv import load_dotenv
import json

import sys
from pathlib import Path

# Добавляем путь к корневой директории проекта
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from services.shared_services.catalog import get_catalog_service, CatalogService
from services.shared_services.prompts import get_prompts_service, PromptsService
from database.models import Audiobook

# Загружаем переменные окружения из корня проекта
env_path = project_root / '.env'
load_dotenv(env_path)

# Инициализация FastAPI приложения
app = FastAPI(
    title="AI Recommender Service",
    description="Core Domain сервис для AI-рекомендаций аудиокниг",
    version="1.0.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене замените на конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Настройка API-клиента для OpenRouter
client = openai.OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    default_headers={
        "HTTP-Referer": "http://localhost:8000/admin/admin.html",
        "X-Title": "Audio Store",
    },
)

# Убираем старые URL, так как будем использовать прямые вызовы
# CATALOG_SERVICE_URL = "http://localhost:8002"
# PROMPTS_SERVICE_URL = "http://localhost:8006"

# Доступные модели LLM
AVAILABLE_MODELS = {
    "gemini-pro": "google/gemini-2.0-flash-001",
    "gemini-flash": "google/gemini-2.0-flash-001",
    "claude-3": "anthropic/claude-3.5-sonnet",
    "gpt-4": "openai/gpt-4-turbo",
    "llama-3": "meta-llama/llama-3-8b-instruct"
}


# Pydantic модели для API
class RecommendationRequest(BaseModel):
    """Запрос на генерацию рекомендаций"""
    prompt: str
    model: str = "gemini-pro"  # Модель по умолчанию


class DescriptionGenerationRequest(BaseModel):
    """Запрос на генерацию описания"""
    model: str = "gemini-pro"  # Модель по умолчанию


class DescriptionGenerationResponse(BaseModel):
    """Ответ с сгенерированным описанием"""
    product_id: int
    generated_description: str
    model: str
    model_alias: str
    success: bool


# Вспомогательные функции (заменяем HTTP-вызовы на прямые)

def get_prompt_from_service(prompt_name: str, prompts_service: PromptsService) -> str:
    """
    Получает промпт из PromptsService.
    """
    prompt = prompts_service.get_prompt_by_name(prompt_name)
    if not prompt:
        raise HTTPException(
            status_code=404,
            detail=f"Промпт '{prompt_name}' не найден"
        )
    return prompt.content

def get_audiobooks_from_catalog(catalog_service: CatalogService) -> list:  
    """
    Получает список аудиокниг из CatalogService.
    """
    # Предполагаем, что сервис каталога может вернуть все книги
    # Если нужна пагинация, здесь ее нужно будет реализовать
    audiobooks = catalog_service.audiobook_repo.get_all()
    # Конвертируем в словари для дальнейшего использования
    return [
        {
            "id": ab.id,
            "title": ab.title,
            "author": {"name": ab.author.name} if ab.author else None,
            "description": ab.description,
            "categories": [{"name": cat.name} for cat in ab.categories]
        }
        for ab in audiobooks
    ]

def create_system_prompt(audiobooks: list, user_prompt: str, prompts_service: PromptsService) -> str:
    """
    Создает системный промпт для LLM, используя промпт из prompts-manager.
    """
    base_prompt = get_prompt_from_service("recommendation_prompt", prompts_service)
    
    books_list_text = "\n".join(
        [f"- {book['title']} (Автор: {book['author']['name'] if book.get('author') else 'Неизвестен'})" for book in audiobooks]
    )
    
    system_prompt = base_prompt.format(
        user_preferences=user_prompt,
        available_books=books_list_text
    )
    
    return system_prompt

def get_audiobook_by_id(product_id: int, catalog_service: CatalogService) -> dict:
    """
    Получает данные конкретной аудиокниги по ID из CatalogService.
    """
    audiobook = catalog_service.get_audiobook_by_id(product_id)
    if not audiobook:
        raise HTTPException(
            status_code=404,
            detail=f"Аудиокнига с ID {product_id} не найдена"
        )
    return {
        "id": audiobook.id,
        "title": audiobook.title,
        "author": {"name": audiobook.author.name} if audiobook.author else None,
        "description": audiobook.description,
        "categories": [{"name": cat.name} for cat in audiobook.categories]
    }

def create_description_prompt(audiobook: dict, prompts_service: PromptsService) -> str:
    """
    Создает промпт для генерации описания аудиокниги, используя промпт из prompts-manager.
    """
    base_prompt = get_prompt_from_service("description_prompt", prompts_service)
    
    title = audiobook.get('title', 'Без названия')
    author_name = audiobook.get('author', {}).get('name', 'Неизвестен') if audiobook.get('author') else 'Неизвестен'
    categories = [cat.get('name', '') for cat in audiobook.get('categories', [])]
    current_description = audiobook.get('description', '')
    
    system_prompt = base_prompt.format(
        title=title,
        author=author_name,
        genre=', '.join(categories) if categories else 'Не указан',
        theme=current_description if current_description else 'Не указана'
    )
    
    return system_prompt

def update_audiobook_description(product_id: int, description: str, catalog_service: CatalogService) -> bool:
    """
    Обновляет описание аудиокниги в CatalogService.
    """
    updated_audiobook = catalog_service.update_audiobook(product_id, description=description)
    return updated_audiobook is not None


# API эндпоинты
@app.get("/")
def root():
    """Корневой эндпоинт"""
    return {
        "message": "AI Recommender Service is running",
        "version": "1.0.0",
        "description": "Core Domain сервис для AI-рекомендаций аудиокниг"
    }

@app.get("/api/v1/models")
def get_available_models():
    """Получить список доступных моделей"""
    return {
        "available_models": AVAILABLE_MODELS,
        "default_model": "gemini-pro",
        "description": "Доступные модели для генерации рекомендаций"
    }

@app.get("/health")
def health_check():
    """Проверка состояния сервиса"""
    api_key = os.getenv("OPENROUTER_API_KEY")
    return {
        "status": "healthy",
        "service": "AI Recommender Service",
        "version": "1.0.0",
        "api_key_configured": bool(api_key),
        "api_key_length": len(api_key) if api_key else 0,
        "api_key_prefix": api_key[:10] + "..." if api_key and len(api_key) > 10 else "None"
    }

@app.post("/api/v1/recommendations/generate")
async def generate_recommendations(request: RecommendationRequest):
    """
    Генерирует персонализированные рекомендации аудиокниг.
    
    Это основной эндпоинт Core Domain, который:
    1. Получает данные из catalog микросервиса (взаимодействие контекстов)
    2. Создает системный промпт (наша интеллектуальная собственность)
    3. Использует LLM для анализа и генерации рекомендаций
    4. Возвращает ответ от модели "как есть"
    """
    
    catalog_service = get_catalog_service()
    prompts_service = get_prompts_service()

    # 1. Получаем каталог аудиокниг
    audiobooks = get_audiobooks_from_catalog(catalog_service)
    
    if not audiobooks:
        raise HTTPException(
            status_code=404,
            detail="Каталог аудиокниг пуст"
        )
    
    # 2. Создаем системный промпт
    system_prompt = create_system_prompt(audiobooks, request.prompt, prompts_service)
    
    # 3. Вызываем LLM через OpenRouter
    try:
        # Получаем полное имя модели
        model_name = AVAILABLE_MODELS.get(request.model, AVAILABLE_MODELS["gemini-pro"])
        print(f"🤖 Используем модель: {request.model} -> {model_name}")
        
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.prompt}
            ],
            max_tokens=1000,
            temperature=0.5
        )
        
        # Проверяем, что ответ содержит валидные данные
        if not response or not response.choices or len(response.choices) == 0:
            raise HTTPException(
                status_code=502,
                detail="LLM сервис вернул пустой ответ"
            )
        
        if not response.choices[0].message or not response.choices[0].message.content:
            raise HTTPException(
                status_code=502,
                detail="LLM сервис вернул ответ без содержимого"
            )
        
        # 4. Возвращаем ответ от модели "как есть"
        return {
            "recommendations": response.choices[0].message.content,
            "model": model_name,
            "model_alias": request.model,
            "total_books_analyzed": len(audiobooks)
        }
        
    except openai.AuthenticationError as e:
        print(f"❌ Ошибка аутентификации с OpenRouter API: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Ошибка аутентификации с LLM сервисом. Проверьте API-ключ."
        )
    except openai.PermissionDeniedError as e:
        print(f"❌ Ошибка доступа к OpenRouter API: {str(e)}")
        raise HTTPException(
            status_code=403,
            detail="Доступ к LLM сервису запрещен. Проверьте права доступа."
        )
    except openai.NotFoundError as e:
        print(f"❌ Модель не найдена в OpenRouter API: {str(e)}")
        raise HTTPException(
            status_code=404,
            detail=f"Модель '{model_name}' не найдена в LLM сервисе"
        )
    except openai.RateLimitError as e:
        print(f"❌ Превышен лимит запросов к OpenRouter API: {str(e)}")
        raise HTTPException(
            status_code=429,
            detail="Превышен лимит запросов к LLM сервису. Попробуйте позже."
        )
    except openai.APITimeoutError as e:
        print(f"❌ Таймаут запроса к OpenRouter API: {str(e)}")
        raise HTTPException(
            status_code=504,
            detail="LLM сервис не отвечает в течение допустимого времени"
        )
    except openai.InternalServerError as e:
        print(f"❌ Внутренняя ошибка OpenRouter API: {str(e)}")
        raise HTTPException(
            status_code=502,
            detail="Внутренняя ошибка LLM сервиса. Попробуйте позже."
        )
    except openai.BadRequestError as e:
        print(f"❌ Неверный запрос к OpenRouter API: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Неверный запрос к LLM сервису: {str(e)}"
        )
    except openai.APIError as e:
        print(f"❌ Общая ошибка OpenRouter API: {str(e)}")
        raise HTTPException(
            status_code=502,
            detail=f"Ошибка LLM сервиса: {str(e)}"
        )
    except Exception as e:
        print(f"❌ Неожиданная ошибка при обращении к LLM: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Неожиданная ошибка при обращении к LLM сервису: {str(e)}"
        )


@app.post("/api/v1/recommendations/generate-description/{product_id}", response_model=DescriptionGenerationResponse)
async def generate_description(product_id: int, request: DescriptionGenerationRequest):
    """
    Оркестратор для процесса "AI-генерация описания".
    
    Этот эндпоинт выполняет полный цикл оркестрации:
    1. Получает данные книги из catalog сервиса
    2. Генерирует описание с помощью LLM
    3. Обновляет описание в catalog сервисе
    4. Возвращает результат клиенту
    
    Это пример оркестрации между ограниченными контекстами.
    """
    
    catalog_service = get_catalog_service()
    prompts_service = get_prompts_service()

    try:
        print(f"🎯 Начинаем оркестрацию генерации описания для книги {product_id}")
        
        # Шаг 1: Получаем данные книги из catalog сервиса
        print(f"📖 Шаг 1: Получение данных книги {product_id}")
        audiobook = get_audiobook_by_id(product_id, catalog_service)
        
        # Шаг 2: Создаем промпт для LLM
        print(f"🤖 Шаг 2: Создание промпта для LLM")
        system_prompt = create_description_prompt(audiobook, prompts_service)
        
        # Шаг 3: Вызываем LLM для генерации описания
        print(f"⚡ Шаг 3: Генерация описания с помощью LLM")
        model_name = AVAILABLE_MODELS.get(request.model, AVAILABLE_MODELS["gemini-pro"])
        print(f"🤖 Используем модель: {request.model} -> {model_name}")
        
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "Создай привлекательное описание для этой аудиокниги."}
                ],
                max_tokens=300,
                temperature=0.5
            )
            
            # Проверяем, что ответ содержит валидные данные
            if not response or not response.choices or len(response.choices) == 0:
                raise HTTPException(
                    status_code=502,
                    detail="LLM сервис вернул пустой ответ"
                )
            
            if not response.choices[0].message or not response.choices[0].message.content:
                raise HTTPException(
                    status_code=502,
                    detail="LLM сервис вернул ответ без содержимого"
                )
            
            generated_description = response.choices[0].message.content.strip()
            print(f"✅ Сгенерировано описание длиной {len(generated_description)} символов")
            
        except openai.AuthenticationError as e:
            print(f"❌ Ошибка аутентификации с OpenRouter API: {str(e)}")
            raise HTTPException(
                status_code=401,
                detail="Ошибка аутентификации с LLM сервисом. Проверьте API-ключ."
            )
        except openai.PermissionDeniedError as e:
            print(f"❌ Ошибка доступа к OpenRouter API: {str(e)}")
            raise HTTPException(
                status_code=403,
                detail="Доступ к LLM сервису запрещен. Проверьте права доступа."
            )
        except openai.NotFoundError as e:
            print(f"❌ Модель не найдена в OpenRouter API: {str(e)}")
            raise HTTPException(
                status_code=404,
                detail=f"Модель '{model_name}' не найдена в LLM сервисе"
            )
        except openai.RateLimitError as e:
            print(f"❌ Превышен лимит запросов к OpenRouter API: {str(e)}")
            raise HTTPException(
                status_code=429,
                detail="Превышен лимит запросов к LLM сервису. Попробуйте позже."
            )
        except openai.APITimeoutError as e:
            print(f"❌ Таймаут запроса к OpenRouter API: {str(e)}")
            raise HTTPException(
                status_code=504,
                detail="LLM сервис не отвечает в течение допустимого времени"
            )
        except openai.InternalServerError as e:
            print(f"❌ Внутренняя ошибка OpenRouter API: {str(e)}")
            raise HTTPException(
                status_code=502,
                detail="Внутренняя ошибка LLM сервиса. Попробуйте позже."
            )
        except openai.BadRequestError as e:
            print(f"❌ Неверный запрос к OpenRouter API: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail=f"Неверный запрос к LLM сервису: {str(e)}"
            )
        except openai.APIError as e:
            print(f"❌ Общая ошибка OpenRouter API: {str(e)}")
            raise HTTPException(
                status_code=502,
                detail=f"Ошибка LLM сервиса: {str(e)}"
            )
        except Exception as e:
            print(f"❌ Неожиданная ошибка при обращении к LLM: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Неожиданная ошибка при обращении к LLM сервису: {str(e)}"
            )
        
        # Шаг 4: Обновляем описание в catalog сервисе
        print(f"🔄 Шаг 4: Обновление описания в catalog сервисе")
        update_success = update_audiobook_description(product_id, generated_description, catalog_service)
        
        if not update_success:
            raise HTTPException(
                status_code=500,
                detail="Не удалось обновить описание в catalog сервисе"
            )
        
        print(f"🎉 Оркестрация завершена успешно для книги {product_id}")
        
        # Возвращаем результат
        return DescriptionGenerationResponse(
            product_id=product_id,
            generated_description=generated_description,
            model=model_name,
            model_alias=request.model,
            success=True
        )
        
    except HTTPException:
        # Перебрасываем HTTP исключения как есть
        raise
    except Exception as e:
        print(f"❌ Ошибка в оркестрации: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка в процессе генерации описания: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
