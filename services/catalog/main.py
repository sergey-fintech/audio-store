# Этот сервис отвечает за управление каталогом аудиокниг, включая:
# - Отображение списка книг с фильтрацией по жанрам, авторам, рейтингу
# - Детальную информацию о книгах (описание, отзывы, рейтинги)
# - Поиск и сортировку книг
# - Управление аудиофрагментами для прослушивания
# - Систему отзывов и рейтингов
# - Рекомендации похожих книг

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import sys
import os

# Добавляем путь к модулю database
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from database.models import Base, Author, Category, Audiobook
from database.repositories import AuthorRepository, CategoryRepository, AudiobookRepository
from database.services import CatalogDomainService
from database.connection import get_db, initialize_database, get_database_info
from schemas import AudiobookCreate, AudiobookUpdate, AudiobookSchema, ErrorResponseSchema

# Инициализация базы данных
initialize_database()

app = FastAPI(title="Catalog Service", version="1.0.0")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене замените на конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Используем функцию get_db из модуля подключения


@app.get("/")
async def root():
    return {"message": "Catalog Service is running"}


@app.get("/health")
async def health_check():
    """Проверка состояния сервиса и базы данных."""
    db_info = get_database_info()
    return {
        "status": "healthy",
        "service": "Catalog Service",
        "version": "1.0.0",
        "database": db_info
    }


# API для авторов
@app.get("/authors", response_model=List[dict])
async def get_authors(db: Session = Depends(get_db)):
    """Получить всех авторов."""
    repo = AuthorRepository(db)
    authors = repo.get_all()
    return [{"id": author.id, "name": author.name} for author in authors]


@app.get("/authors/{author_id}", response_model=dict)
async def get_author(author_id: int, db: Session = Depends(get_db)):
    """Получить автора по ID."""
    repo = AuthorRepository(db)
    author = repo.get_by_id(author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Автор не найден")
    return {"id": author.id, "name": author.name}


@app.post("/authors", response_model=dict)
async def create_author(name: str, db: Session = Depends(get_db)):
    """Создать нового автора."""
    repo = AuthorRepository(db)
    author = repo.create(name)
    return {"id": author.id, "name": author.name}


# API для категорий
@app.get("/categories", response_model=List[dict])
async def get_categories(db: Session = Depends(get_db)):
    """Получить все категории."""
    repo = CategoryRepository(db)
    categories = repo.get_all()
    return [{"id": category.id, "name": category.name} for category in categories]


@app.get("/categories/{category_id}", response_model=dict)
async def get_category(category_id: int, db: Session = Depends(get_db)):
    """Получить категорию по ID."""
    repo = CategoryRepository(db)
    category = repo.get_by_id(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    return {"id": category.id, "name": category.name}


@app.post("/categories", response_model=dict)
async def create_category(name: str, db: Session = Depends(get_db)):
    """Создать новую категорию."""
    repo = CategoryRepository(db)
    category = repo.create(name)
    return {"id": category.id, "name": category.name}


# API для аудиокниг
@app.get("/audiobooks", response_model=List[dict])
@app.get("/api/v1/audiobooks", response_model=List[dict])
async def get_audiobooks(
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Получить все аудиокниги с пагинацией."""
    repo = AudiobookRepository(db)
    audiobooks = repo.get_all(limit=limit, offset=offset)
    return [
        {
            "id": ab.id,
            "title": ab.title,
            "description": ab.description,
            "price": float(ab.price),
            "cover_image_url": ab.cover_image_url,
            "author": {"id": ab.author.id, "name": ab.author.name} if ab.author else None,
            "categories": [{"id": cat.id, "name": cat.name} for cat in ab.categories]
        }
        for ab in audiobooks
    ]


@app.get("/api/v1/search", response_model=List[dict])
async def search_audiobooks(
    q: str,
    limit: Optional[int] = 100,
    db: Session = Depends(get_db)
):
    """Поиск аудиокниг по названию, автору или описанию."""
    repo = AudiobookRepository(db)
    audiobooks = repo.search(q, limit=limit)
    return [
        {
            "id": ab.id,
            "title": ab.title,
            "description": ab.description,
            "price": float(ab.price),
            "cover_image_url": ab.cover_image_url,
            "author": {"id": ab.author.id, "name": ab.author.name} if ab.author else None,
            "categories": [{"id": cat.id, "name": cat.name} for cat in ab.categories]
        }
        for ab in audiobooks
    ]


@app.get("/audiobooks/{audiobook_id}", response_model=dict)
@app.get("/api/v1/audiobooks/{audiobook_id}", response_model=dict)
async def get_audiobook(audiobook_id: int, db: Session = Depends(get_db)):
    """Получить аудиокнигу по ID."""
    repo = AudiobookRepository(db)
    audiobook = repo.get_by_id(audiobook_id)
    if not audiobook:
        raise HTTPException(status_code=404, detail="Аудиокнига не найдена")
    
    return {
        "id": audiobook.id,
        "title": audiobook.title,
        "description": audiobook.description,
        "price": float(audiobook.price),
        "cover_image_url": audiobook.cover_image_url,
        "author": {"id": audiobook.author.id, "name": audiobook.author.name} if audiobook.author else None,
        "categories": [{"id": cat.id, "name": cat.name} for cat in audiobook.categories]
    }


@app.post("/api/v1/audiobooks", response_model=dict)
async def create_audiobook(audiobook_data: AudiobookCreate, db: Session = Depends(get_db)):
    """Создать новую аудиокнигу."""
    repo = AudiobookRepository(db)
    
    # Проверяем существование автора
    author_repo = AuthorRepository(db)
    author = author_repo.get_by_id(audiobook_data.author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Автор не найден")
    
    # Создаем аудиокнигу
    audiobook = repo.create(
        title=audiobook_data.title,
        author_id=audiobook_data.author_id,
        price=float(audiobook_data.price),
        description=audiobook_data.description,
        cover_image_url=audiobook_data.cover_image_url
    )
    
    # Добавляем категории, если указаны
    if audiobook_data.category_ids:
        category_repo = CategoryRepository(db)
        for category_id in audiobook_data.category_ids:
            category = category_repo.get_by_id(category_id)
            if category:
                repo.add_category(audiobook.id, category_id)
    
    # Получаем обновленную аудиокнигу с категориями
    updated_audiobook = repo.get_by_id(audiobook.id)
    
    return {
        "id": updated_audiobook.id,
        "title": updated_audiobook.title,
        "description": updated_audiobook.description,
        "price": float(updated_audiobook.price),
        "cover_image_url": updated_audiobook.cover_image_url,
        "author": {"id": updated_audiobook.author.id, "name": updated_audiobook.author.name} if updated_audiobook.author else None,
        "categories": [{"id": cat.id, "name": cat.name} for cat in updated_audiobook.categories]
    }


@app.put("/api/v1/audiobooks/{audiobook_id}", response_model=dict)
async def update_audiobook(audiobook_id: int, audiobook_data: AudiobookUpdate, db: Session = Depends(get_db)):
    """Обновить аудиокнигу по ID."""
    repo = AudiobookRepository(db)
    
    # Проверяем существование аудиокниги
    existing_audiobook = repo.get_by_id(audiobook_id)
    if not existing_audiobook:
        raise HTTPException(status_code=404, detail="Аудиокнига не найдена")
    
    # Проверяем существование автора, если указан
    if audiobook_data.author_id is not None:
        author_repo = AuthorRepository(db)
        author = author_repo.get_by_id(audiobook_data.author_id)
        if not author:
            raise HTTPException(status_code=404, detail="Автор не найден")
    
    # Подготавливаем данные для обновления
    update_data = {}
    if audiobook_data.title is not None:
        update_data['title'] = audiobook_data.title
    if audiobook_data.author_id is not None:
        update_data['author_id'] = audiobook_data.author_id
    if audiobook_data.price is not None:
        update_data['price'] = float(audiobook_data.price)
    if audiobook_data.description is not None:
        update_data['description'] = audiobook_data.description
    if audiobook_data.cover_image_url is not None:
        update_data['cover_image_url'] = audiobook_data.cover_image_url
    
    # Обновляем аудиокнигу
    updated_audiobook = repo.update(audiobook_id, **update_data)
    
    # Обновляем категории, если указаны
    if audiobook_data.category_ids is not None:
        # Удаляем все существующие категории
        for category in existing_audiobook.categories:
            repo.remove_category(audiobook_id, category.id)
        
        # Добавляем новые категории
        category_repo = CategoryRepository(db)
        for category_id in audiobook_data.category_ids:
            category = category_repo.get_by_id(category_id)
            if category:
                repo.add_category(audiobook_id, category_id)
    
    # Получаем обновленную аудиокнигу
    final_audiobook = repo.get_by_id(audiobook_id)
    
    return {
        "id": final_audiobook.id,
        "title": final_audiobook.title,
        "description": final_audiobook.description,
        "price": float(final_audiobook.price),
        "cover_image_url": final_audiobook.cover_image_url,
        "author": {"id": final_audiobook.author.id, "name": final_audiobook.author.name} if final_audiobook.author else None,
        "categories": [{"id": cat.id, "name": cat.name} for cat in final_audiobook.categories]
    }


@app.delete("/api/v1/audiobooks/{audiobook_id}")
async def delete_audiobook(audiobook_id: int, db: Session = Depends(get_db)):
    """Удалить аудиокнигу по ID."""
    repo = AudiobookRepository(db)
    
    # Проверяем существование аудиокниги
    existing_audiobook = repo.get_by_id(audiobook_id)
    if not existing_audiobook:
        raise HTTPException(status_code=404, detail="Аудиокнига не найдена")
    
    # Удаляем аудиокнигу
    success = repo.delete(audiobook_id)
    
    if success:
        return {"message": "Аудиокнига успешно удалена", "id": audiobook_id}
    else:
        raise HTTPException(status_code=500, detail="Ошибка при удалении аудиокниги")


@app.post("/audiobooks", response_model=dict)
async def create_audiobook(
    title: str,
    author_id: int,
    price: float,
    description: Optional[str] = None,
    cover_image_url: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Создать новую аудиокнигу."""
    repo = AudiobookRepository(db)
    audiobook = repo.create(
        title=title,
        author_id=author_id,
        price=price,
        description=description,
        cover_image_url=cover_image_url
    )
    
    return {
        "id": audiobook.id,
        "title": audiobook.title,
        "description": audiobook.description,
        "price": float(audiobook.price),
        "cover_image_url": audiobook.cover_image_url,
        "author_id": audiobook.author_id
    }


@app.get("/audiobooks/author/{author_id}", response_model=List[dict])
async def get_audiobooks_by_author(author_id: int, db: Session = Depends(get_db)):
    """Получить аудиокниги по автору."""
    repo = AudiobookRepository(db)
    audiobooks = repo.get_by_author(author_id)
    return [
        {
            "id": ab.id,
            "title": ab.title,
            "description": ab.description,
            "price": float(ab.price),
            "cover_image_url": ab.cover_image_url,
            "author": {"id": ab.author.id, "name": ab.author.name} if ab.author else None,
            "categories": [{"id": cat.id, "name": cat.name} for cat in ab.categories]
        }
        for ab in audiobooks
    ]


@app.get("/audiobooks/category/{category_id}", response_model=List[dict])
async def get_audiobooks_by_category(category_id: int, db: Session = Depends(get_db)):
    """Получить аудиокниги по категории."""
    repo = AudiobookRepository(db)
    audiobooks = repo.get_by_category(category_id)
    return [
        {
            "id": ab.id,
            "title": ab.title,
            "description": ab.description,
            "price": float(ab.price),
            "cover_image_url": ab.cover_image_url,
            "author": {"id": ab.author.id, "name": ab.author.name} if ab.author else None,
            "categories": [{"id": cat.id, "name": cat.name} for cat in ab.categories]
        }
        for ab in audiobooks
    ]


# API для доменного сервиса
@app.get("/catalog/statistics", response_model=dict)
async def get_catalog_statistics(db: Session = Depends(get_db)):
    """Получить статистику каталога."""
    service = CatalogDomainService(db)
    return service.get_catalog_statistics()


@app.get("/catalog/authors/{author_id}/summary", response_model=dict)
async def get_author_summary(author_id: int, db: Session = Depends(get_db)):
    """Получить сводку работ автора."""
    service = CatalogDomainService(db)
    summary = service.get_author_works_summary(author_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Автор не найден")
    return summary


@app.get("/catalog/categories/{category_id}/analysis", response_model=dict)
async def get_category_analysis(category_id: int, db: Session = Depends(get_db)):
    """Получить анализ категории."""
    service = CatalogDomainService(db)
    analysis = service.get_category_analysis(category_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    return analysis


@app.post("/catalog/audiobooks/comprehensive", response_model=dict)
async def create_audiobook_comprehensive(
    title: str,
    author_name: str,
    price: float,
    category_names: Optional[List[str]] = None,
    description: Optional[str] = None,
    cover_image_url: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Создать аудиокнигу с автором и категориями через доменный сервис."""
    service = CatalogDomainService(db)
    audiobook = service.create_audiobook_with_author_and_categories(
        title=title,
        author_name=author_name,
        price=price,
        category_names=category_names,
        description=description,
        cover_image_url=cover_image_url
    )
    
    return {
        "id": audiobook.id,
        "title": audiobook.title,
        "description": audiobook.description,
        "price": float(audiobook.price),
        "cover_image_url": audiobook.cover_image_url,
        "author": {"id": audiobook.author.id, "name": audiobook.author.name} if audiobook.author else None,
        "categories": [{"id": cat.id, "name": cat.name} for cat in audiobook.categories]
    }


@app.get("/catalog/audiobooks/comprehensive-search", response_model=List[dict])
async def search_audiobooks_comprehensive(
    query: Optional[str] = None,
    author_id: Optional[int] = None,
    category_ids: Optional[List[int]] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Комплексный поиск аудиокниг с множественными фильтрами."""
    service = CatalogDomainService(db)
    audiobooks = service.search_audiobooks_comprehensive(
        query=query,
        author_id=author_id,
        category_ids=category_ids,
        min_price=min_price,
        max_price=max_price,
        limit=limit,
        offset=offset
    )
    
    return [
        {
            "id": ab.id,
            "title": ab.title,
            "description": ab.description,
            "price": float(ab.price),
            "cover_image_url": ab.cover_image_url,
            "author": {"id": ab.author.id, "name": ab.author.name} if ab.author else None,
            "categories": [{"id": cat.id, "name": cat.name} for cat in ab.categories]
        }
        for ab in audiobooks
    ]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002) 