"""
Pydantic схемы для API прикладного слоя домена "Каталог".

Эти схемы определяют контракт данных для публичного API,
обеспечивая чистоту и валидацию данных.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime
from decimal import Decimal


class AuthorSchema(BaseModel):
    """Схема для данных автора."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="Уникальный идентификатор автора")
    name: str = Field(..., description="Имя автора", max_length=255)
    created_at: Optional[datetime] = Field(None, description="Дата создания записи")
    updated_at: Optional[datetime] = Field(None, description="Дата последнего обновления")


class CategorySchema(BaseModel):
    """Схема для данных категории."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="Уникальный идентификатор категории")
    name: str = Field(..., description="Название категории", max_length=100)
    created_at: Optional[datetime] = Field(None, description="Дата создания записи")
    updated_at: Optional[datetime] = Field(None, description="Дата последнего обновления")


class AudiobookSchema(BaseModel):
    """Схема для данных аудиокниги с полной связанной информацией."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="Уникальный идентификатор аудиокниги")
    title: str = Field(..., description="Название аудиокниги", max_length=255)
    description: Optional[str] = Field(None, description="Описание аудиокниги")
    price: Decimal = Field(..., description="Цена аудиокниги", ge=0)
    cover_image_url: Optional[str] = Field(None, description="URL обложки", max_length=500)
    author: AuthorSchema = Field(..., description="Информация об авторе")
    categories: List[CategorySchema] = Field(default_factory=list, description="Список категорий")
    created_at: Optional[datetime] = Field(None, description="Дата создания записи")
    updated_at: Optional[datetime] = Field(None, description="Дата последнего обновления")


class AudiobookListSchema(BaseModel):
    """Схема для списка аудиокниг с пагинацией."""
    
    items: List[AudiobookSchema] = Field(..., description="Список аудиокниг")
    total: int = Field(..., description="Общее количество аудиокниг")
    limit: Optional[int] = Field(None, description="Лимит записей на страницу")
    offset: Optional[int] = Field(None, description="Смещение для пагинации")
    has_more: bool = Field(..., description="Есть ли еще записи")


class CreateAuthorRequest(BaseModel):
    """Схема для создания автора."""
    
    name: str = Field(..., description="Имя автора", max_length=255)


class CreateCategoryRequest(BaseModel):
    """Схема для создания категории."""
    
    name: str = Field(..., description="Название категории", max_length=100)


class CreateAudiobookRequest(BaseModel):
    """Схема для создания аудиокниги."""
    
    title: str = Field(..., description="Название аудиокниги", max_length=255)
    author_id: int = Field(..., description="ID автора")
    price: Decimal = Field(..., description="Цена аудиокниги", ge=0)
    description: Optional[str] = Field(None, description="Описание аудиокниги")
    cover_image_url: Optional[str] = Field(None, description="URL обложки", max_length=500)
    category_ids: Optional[List[int]] = Field(None, description="Список ID категорий")


class CreateAudiobookComprehensiveRequest(BaseModel):
    """Схема для комплексного создания аудиокниги с автором и категориями."""
    
    title: str = Field(..., description="Название аудиокниги", max_length=255)
    author_name: str = Field(..., description="Имя автора", max_length=255)
    price: Decimal = Field(..., description="Цена аудиокниги", ge=0)
    description: Optional[str] = Field(None, description="Описание аудиокниги")
    cover_image_url: Optional[str] = Field(None, description="URL обложки", max_length=500)
    category_names: Optional[List[str]] = Field(None, description="Список названий категорий")


class SearchAudiobooksRequest(BaseModel):
    """Схема для поиска аудиокниг."""
    
    query: Optional[str] = Field(None, description="Поисковый запрос")
    author_id: Optional[int] = Field(None, description="ID автора для фильтрации")
    category_ids: Optional[List[int]] = Field(None, description="Список ID категорий для фильтрации")
    min_price: Optional[Decimal] = Field(None, description="Минимальная цена", ge=0)
    max_price: Optional[Decimal] = Field(None, description="Максимальная цена", ge=0)
    limit: Optional[int] = Field(None, description="Лимит записей", ge=1, le=100)
    offset: Optional[int] = Field(None, description="Смещение для пагинации", ge=0)


class CatalogStatisticsSchema(BaseModel):
    """Схема для статистики каталога."""
    
    total_authors: int = Field(..., description="Общее количество авторов")
    total_categories: int = Field(..., description="Общее количество категорий")
    total_audiobooks: int = Field(..., description="Общее количество аудиокниг")
    average_price: Decimal = Field(..., description="Средняя цена аудиокниг")
    category_distribution: List[dict] = Field(..., description="Распределение по категориям")


class AuthorSummarySchema(BaseModel):
    """Схема для сводки работ автора."""
    
    author: AuthorSchema = Field(..., description="Информация об авторе")
    total_works: int = Field(..., description="Общее количество работ")
    total_value: Decimal = Field(..., description="Общая стоимость работ")
    average_price: Decimal = Field(..., description="Средняя цена работы")
    category_distribution: dict = Field(..., description="Распределение по категориям")
    audiobooks: List[AudiobookSchema] = Field(..., description="Список аудиокниг автора")


class CategoryAnalysisSchema(BaseModel):
    """Схема для анализа категории."""
    
    category: CategorySchema = Field(..., description="Информация о категории")
    total_audiobooks: int = Field(..., description="Общее количество аудиокниг в категории")
    total_value: Decimal = Field(..., description="Общая стоимость аудиокниг в категории")
    average_price: Decimal = Field(..., description="Средняя цена аудиокниг в категории")
    top_authors: List[dict] = Field(..., description="Топ авторов в категории")
    audiobooks: List[AudiobookSchema] = Field(..., description="Список аудиокниг в категории")


class HealthCheckSchema(BaseModel):
    """Схема для проверки состояния сервиса."""
    
    status: str = Field(..., description="Статус сервиса")
    service: str = Field(..., description="Название сервиса")
    version: str = Field(..., description="Версия сервиса")
    database: dict = Field(..., description="Информация о базе данных")


class ErrorResponseSchema(BaseModel):
    """Схема для ошибок API."""
    
    error: str = Field(..., description="Описание ошибки")
    detail: Optional[str] = Field(None, description="Детали ошибки")
    status_code: int = Field(..., description="HTTP код ошибки") 