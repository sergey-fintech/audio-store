"""
FastAPI приложение для прикладного слоя домена "Каталог".

Это приложение реализует API-эндпоинты для работы с каталогом аудиокниг,
используя сервисы прикладного слоя и DTO схемы.
"""

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import sys
import os

# Добавляем путь к модулю database
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from database.connection import get_db, initialize_database, get_database_info
from schemas import (
    AudiobookSchema, AuthorSchema, CategorySchema, AudiobookListSchema,
    CreateAuthorRequest, CreateCategoryRequest, CreateAudiobookRequest,
    CreateAudiobookComprehensiveRequest, SearchAudiobooksRequest,
    CatalogStatisticsSchema, AuthorSummarySchema, CategoryAnalysisSchema,
    HealthCheckSchema, ErrorResponseSchema
)
from services import CatalogApplicationService

# Инициализация базы данных
initialize_database()

# Создание FastAPI приложения
app = FastAPI(
    title="Catalog Service API",
    description="API для управления каталогом аудиокниг",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене замените на конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Функция для получения сервиса прикладного слоя
def get_catalog_service(db: Session = Depends(get_db)) -> CatalogApplicationService:
    """Получить сервис прикладного слоя для работы с каталогом."""
    return CatalogApplicationService(db)


# Обработчики ошибок
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Обработчик HTTP исключений."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponseSchema(
            error=exc.detail,
            status_code=exc.status_code
        ).model_dump()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Обработчик общих исключений."""
    return JSONResponse(
        status_code=500,
        content=ErrorResponseSchema(
            error="Внутренняя ошибка сервера",
            detail=str(exc),
            status_code=500
        ).model_dump()
    )


# Базовые эндпоинты
@app.get("/", response_model=dict)
async def root():
    """Корневой эндпоинт."""
    return {
        "message": "Catalog Service API",
        "version": "1.0.0",
        "docs": "/api/docs"
    }


@app.get("/health", response_model=HealthCheckSchema)
async def health_check():
    """Проверка состояния сервиса и базы данных."""
    db_info = get_database_info()
    return HealthCheckSchema(
        status="healthy",
        service="Catalog Service",
        version="1.0.0",
        database=db_info
    )


# API v1 эндпоинты
@app.get("/api/v1/audiobooks", response_model=AudiobookListSchema)
async def get_audiobooks(
    limit: Optional[int] = Query(None, ge=1, le=100, description="Лимит записей"),
    offset: Optional[int] = Query(None, ge=0, description="Смещение для пагинации"),
    service: CatalogApplicationService = Depends(get_catalog_service)
):
    """
    Получить список всех аудиокниг с полной связанной информацией.
    
    Возвращает список аудиокниг с информацией об авторах и категориях,
    поддерживает пагинацию.
    """
    return service.get_all_audiobooks(limit=limit, offset=offset)


@app.get("/api/v1/audiobooks/{audiobook_id}", response_model=AudiobookSchema)
async def get_audiobook(
    audiobook_id: int,
    service: CatalogApplicationService = Depends(get_catalog_service)
):
    """
    Получить аудиокнигу по ID с полной связанной информацией.
    
    Возвращает аудиокнигу с информацией об авторе и категориях.
    """
    audiobook = service.get_audiobook_by_id(audiobook_id)
    if not audiobook:
        raise HTTPException(status_code=404, detail="Аудиокнига не найдена")
    return audiobook


@app.post("/api/v1/audiobooks", response_model=AudiobookSchema)
async def create_audiobook(
    request: CreateAudiobookRequest,
    service: CatalogApplicationService = Depends(get_catalog_service)
):
    """
    Создать новую аудиокнигу.
    
    Создает аудиокнигу с указанными параметрами и возвращает
    созданную аудиокнигу с полной информацией.
    """
    try:
        return service.create_audiobook(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка создания аудиокниги: {str(e)}")


@app.post("/api/v1/audiobooks/comprehensive", response_model=AudiobookSchema)
async def create_audiobook_comprehensive(
    request: CreateAudiobookComprehensiveRequest,
    service: CatalogApplicationService = Depends(get_catalog_service)
):
    """
    Создать аудиокнигу с автоматическим созданием автора и категорий.
    
    Создает аудиокнигу, автоматически создавая автора и категории,
    если они не существуют.
    """
    try:
        return service.create_audiobook_comprehensive(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка создания аудиокниги: {str(e)}")


@app.post("/api/v1/audiobooks/search", response_model=AudiobookListSchema)
async def search_audiobooks(
    request: SearchAudiobooksRequest,
    service: CatalogApplicationService = Depends(get_catalog_service)
):
    """
    Поиск аудиокниг с множественными фильтрами.
    
    Поддерживает поиск по тексту, фильтрацию по автору, категориям,
    диапазону цен с пагинацией.
    """
    return service.search_audiobooks(request)


@app.get("/api/v1/authors", response_model=List[AuthorSchema])
async def get_authors(
    service: CatalogApplicationService = Depends(get_catalog_service)
):
    """
    Получить всех авторов.
    
    Возвращает список всех авторов в системе.
    """
    return service.get_all_authors()


@app.get("/api/v1/authors/{author_id}", response_model=AuthorSchema)
async def get_author(
    author_id: int,
    service: CatalogApplicationService = Depends(get_catalog_service)
):
    """
    Получить автора по ID.
    
    Возвращает информацию об авторе по его ID.
    """
    author = service.get_author_by_id(author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Автор не найден")
    return author


@app.post("/api/v1/authors", response_model=AuthorSchema)
async def create_author(
    request: CreateAuthorRequest,
    service: CatalogApplicationService = Depends(get_catalog_service)
):
    """
    Создать нового автора.
    
    Создает нового автора с указанным именем.
    """
    try:
        return service.create_author(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка создания автора: {str(e)}")


@app.get("/api/v1/authors/{author_id}/audiobooks", response_model=List[AudiobookSchema])
async def get_audiobooks_by_author(
    author_id: int,
    service: CatalogApplicationService = Depends(get_catalog_service)
):
    """
    Получить аудиокниги по автору.
    
    Возвращает все аудиокниги указанного автора.
    """
    return service.get_audiobooks_by_author(author_id)


@app.get("/api/v1/authors/{author_id}/summary", response_model=AuthorSummarySchema)
async def get_author_summary(
    author_id: int,
    service: CatalogApplicationService = Depends(get_catalog_service)
):
    """
    Получить сводку работ автора.
    
    Возвращает статистику и список работ автора.
    """
    summary = service.get_author_summary(author_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Автор не найден")
    return summary


@app.get("/api/v1/categories", response_model=List[CategorySchema])
async def get_categories(
    service: CatalogApplicationService = Depends(get_catalog_service)
):
    """
    Получить все категории.
    
    Возвращает список всех категорий в системе.
    """
    return service.get_all_categories()


@app.get("/api/v1/categories/{category_id}", response_model=CategorySchema)
async def get_category(
    category_id: int,
    service: CatalogApplicationService = Depends(get_catalog_service)
):
    """
    Получить категорию по ID.
    
    Возвращает информацию о категории по её ID.
    """
    category = service.get_category_by_id(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    return category


@app.post("/api/v1/categories", response_model=CategorySchema)
async def create_category(
    request: CreateCategoryRequest,
    service: CatalogApplicationService = Depends(get_catalog_service)
):
    """
    Создать новую категорию.
    
    Создает новую категорию с указанным названием.
    """
    try:
        return service.create_category(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка создания категории: {str(e)}")


@app.get("/api/v1/categories/{category_id}/audiobooks", response_model=List[AudiobookSchema])
async def get_audiobooks_by_category(
    category_id: int,
    service: CatalogApplicationService = Depends(get_catalog_service)
):
    """
    Получить аудиокниги по категории.
    
    Возвращает все аудиокниги в указанной категории.
    """
    return service.get_audiobooks_by_category(category_id)


@app.get("/api/v1/categories/{category_id}/analysis", response_model=CategoryAnalysisSchema)
async def get_category_analysis(
    category_id: int,
    service: CatalogApplicationService = Depends(get_catalog_service)
):
    """
    Получить анализ категории.
    
    Возвращает статистику и анализ указанной категории.
    """
    analysis = service.get_category_analysis(category_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    return analysis


@app.get("/api/v1/catalog/statistics", response_model=CatalogStatisticsSchema)
async def get_catalog_statistics(
    service: CatalogApplicationService = Depends(get_catalog_service)
):
    """
    Получить статистику каталога.
    
    Возвращает общую статистику по каталогу аудиокниг.
    """
    return service.get_catalog_statistics()


# Запуск приложения
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002) 