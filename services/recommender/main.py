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

# Загружаем переменные окружения
load_dotenv()

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
)

# Конфигурация
CATALOG_SERVICE_URL = "http://localhost:8002"  # URL микросервиса catalog
PROMPTS_SERVICE_URL = "http://localhost:8006"  # URL микросервиса prompts-manager

# Доступные модели LLM
AVAILABLE_MODELS = {
    "gemini-pro": "google/gemini-pro-1.5",
    "gemini-flash": "google/gemini-flash-1.5-8b", 
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


# Вспомогательные функции
async def fetch_prompt_from_service(prompt_name: str) -> str:
    """
    Получает промпт из микросервиса prompts-manager.
    Это взаимодействие между ограниченными контекстами (Anti-Corruption Layer).
    """
    try:
        url = f"{PROMPTS_SERVICE_URL}/prompts/name/{prompt_name}"
        print(f"🔍 Запрос к Prompts Service: {url}")
        
        def make_request():
            return requests.get(url, timeout=10.0)
        
        response = await asyncio.to_thread(make_request)
        print(f"📡 Ответ от Prompts Service: статус {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            prompt_content = data.get('content', '')
            print(f"✅ Получен промпт '{prompt_name}' длиной {len(prompt_content)} символов")
            return prompt_content
        elif response.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail=f"Промпт '{prompt_name}' не найден в prompts-manager"
            )
        else:
            print(f"❌ Ошибка {response.status_code}: {response.text[:100]}")
            raise HTTPException(
                status_code=503,
                detail=f"Prompts сервис вернул ошибку {response.status_code}: {response.text}"
            )
        
    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=503,
            detail="Prompts сервис не отвечает в течение 10 секунд"
        )
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=503,
            detail=f"Ошибка подключения к prompts сервису: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Неожиданная ошибка при получении промпта: {str(e)}"
        )


async def fetch_audiobooks_from_catalog() -> list:  
    """
    Получает список аудиокниг из микросервиса catalog.
    Это взаимодействие между ограниченными контекстами (Anti-Corruption Layer).
    """
    try:
        # Используем правильный эндпоинт catalog сервиса (как в cart сервисе)
        url = f"{CATALOG_SERVICE_URL}/api/v1/audiobooks"
        print(f"🔍 Запрос к Catalog Service: {url}")
        
        # Используем requests в отдельном потоке для асинхронности
        def make_request():
            return requests.get(url, timeout=10.0)
        
        response = await asyncio.to_thread(make_request)
        print(f"📡 Ответ от Catalog Service: статус {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Получены данные: {len(data) if isinstance(data, list) else 'не список'}")
            if isinstance(data, list) and len(data) > 0:
                return data
            elif isinstance(data, dict):
                print(f"📝 Ответ не список: {data}")
        else:
            print(f"❌ Ошибка {response.status_code}: {response.text[:100]}")
            raise HTTPException(
                status_code=503,
                detail=f"Catalog сервис вернул ошибку {response.status_code}: {response.text}"
            )
        
    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=503,
            detail="Catalog сервис не отвечает в течение 10 секунд"
        )
    except requests.exceptions.HTTPError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Catalog сервис вернул ошибку {e.response.status_code}: {e.response.text}"
        )
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=503,
            detail=f"Ошибка подключения к catalog сервису: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Неожиданная ошибка: {str(e)}"
        )


async def create_system_prompt(audiobooks: list, user_prompt: str) -> str:
    """
    Создает системный промпт для LLM, используя промпт из prompts-manager.
    Это наша интеллектуальная собственность - Core Domain логика.
    """
    # Получаем базовый промпт из prompts-manager
    base_prompt = await fetch_prompt_from_service("recommendation_prompt")
    
    # Формируем JSON с каталогом книг
    books_json = []
    for book in audiobooks:
        book_data = {
            "id": book['id'],
            "title": book['title'],
            "author": book['author']['name'] if book['author'] else 'Неизвестен',
            "description": book['description'] or 'Описание отсутствует',
            "price": book['price'],
            "categories": [cat['name'] for cat in book['categories']] if book['categories'] else []
        }
        books_json.append(book_data)
    
    # Форматируем промпт с данными
    system_prompt = base_prompt.format(
        user_preferences=user_prompt,
        available_books=books_json
    )
    
    return system_prompt


async def fetch_audiobook_by_id(product_id: int) -> dict:
    """
    Получает данные конкретной аудиокниги по ID из микросервиса catalog.
    Это взаимодействие между ограниченными контекстами (Anti-Corruption Layer).
    """
    try:
        url = f"{CATALOG_SERVICE_URL}/api/v1/audiobooks/{product_id}"
        print(f"🔍 Запрос к Catalog Service для книги {product_id}: {url}")
        
        def make_request():
            return requests.get(url, timeout=10.0)
        
        response = await asyncio.to_thread(make_request)
        print(f"📡 Ответ от Catalog Service: статус {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Получены данные книги: {data.get('title', 'Без названия')}")
            return data
        elif response.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail=f"Аудиокнига с ID {product_id} не найдена"
            )
        else:
            print(f"❌ Ошибка {response.status_code}: {response.text[:100]}")
            raise HTTPException(
                status_code=503,
                detail=f"Catalog сервис вернул ошибку {response.status_code}: {response.text}"
            )
        
    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=503,
            detail="Catalog сервис не отвечает в течение 10 секунд"
        )
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=503,
            detail=f"Ошибка подключения к catalog сервису: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Неожиданная ошибка: {str(e)}"
        )


async def create_description_prompt(audiobook: dict) -> str:
    """
    Создает промпт для генерации описания аудиокниги, используя промпт из prompts-manager.
    Это наша интеллектуальная собственность - Core Domain логика.
    """
    # Получаем базовый промпт из prompts-manager
    base_prompt = await fetch_prompt_from_service("description_prompt")
    
    title = audiobook.get('title', 'Без названия')
    author_name = audiobook.get('author', {}).get('name', 'Неизвестен') if audiobook.get('author') else 'Неизвестен'
    categories = [cat.get('name', '') for cat in audiobook.get('categories', [])]
    current_description = audiobook.get('description', '')
    
    # Форматируем промпт с данными
    system_prompt = base_prompt.format(
        title=title,
        author=author_name,
        genre=', '.join(categories) if categories else 'Не указан',
        theme=current_description if current_description else 'Не указана'
    )
    
    return system_prompt


async def update_audiobook_description(product_id: int, description: str) -> bool:
    """
    Обновляет описание аудиокниги в микросервисе catalog.
    Это взаимодействие между ограниченными контекстами (Anti-Corruption Layer).
    
    Использует PUT метод с полной схемой AudiobookUpdate.
    """
    try:
        url = f"{CATALOG_SERVICE_URL}/api/v1/audiobooks/{product_id}"
        print(f"🔄 Обновление описания книги {product_id}: {url}")
        
        # Создаем payload согласно схеме AudiobookUpdate
        # Все поля опциональны, передаем только description
        payload = {
            "description": description
        }
        
        def make_request():
            return requests.put(url, json=payload, timeout=10.0)
        
        response = await asyncio.to_thread(make_request)
        print(f"📡 Ответ от Catalog Service при обновлении: статус {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ Описание успешно обновлено для книги {product_id}")
            return True
        elif response.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail=f"Аудиокнига с ID {product_id} не найдена"
            )
        else:
            print(f"❌ Ошибка при обновлении {response.status_code}: {response.text[:100]}")
            raise HTTPException(
                status_code=503,
                detail=f"Catalog сервис вернул ошибку при обновлении {response.status_code}: {response.text}"
            )
        
    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=503,
            detail="Catalog сервис не отвечает в течение 10 секунд"
        )
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=503,
            detail=f"Ошибка подключения к catalog сервису: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Неожиданная ошибка при обновлении: {str(e)}"
        )


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
    
    # 1. Получаем каталог аудиокниг из catalog микросервиса (Anti-Corruption Layer)
    audiobooks = await fetch_audiobooks_from_catalog()
    
    if not audiobooks:
        raise HTTPException(
            status_code=404,
            detail="Каталог аудиокниг пуст"
        )
    
    # 2. Создаем системный промпт (наша Core Domain логика)
    system_prompt = await create_system_prompt(audiobooks, request.prompt)
    
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
            max_tokens=1500,
            temperature=0.7
        )
        
        # 4. Возвращаем ответ от модели "как есть"
        return {
            "recommendations": response.choices[0].message.content,
            "model": model_name,
            "model_alias": request.model,
            "total_books_analyzed": len(audiobooks)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при обращении к LLM: {str(e)}"
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
    
    try:
        print(f"🎯 Начинаем оркестрацию генерации описания для книги {product_id}")
        
        # Шаг 1: Получаем данные книги из catalog сервиса
        print(f"📖 Шаг 1: Получение данных книги {product_id}")
        audiobook = await fetch_audiobook_by_id(product_id)
        
        # Шаг 2: Создаем промпт для LLM
        print(f"🤖 Шаг 2: Создание промпта для LLM")
        system_prompt = await create_description_prompt(audiobook)
        
        # Шаг 3: Вызываем LLM для генерации описания
        print(f"⚡ Шаг 3: Генерация описания с помощью LLM")
        model_name = AVAILABLE_MODELS.get(request.model, AVAILABLE_MODELS["gemini-pro"])
        print(f"🤖 Используем модель: {request.model} -> {model_name}")
        
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Создай привлекательное описание для этой аудиокниги."}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        generated_description = response.choices[0].message.content.strip()
        print(f"✅ Сгенерировано описание длиной {len(generated_description)} символов")
        
        # Шаг 4: Обновляем описание в catalog сервисе
        print(f"🔄 Шаг 4: Обновление описания в catalog сервисе")
        update_success = await update_audiobook_description(product_id, generated_description)
        
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
