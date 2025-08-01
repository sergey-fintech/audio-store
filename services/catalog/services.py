"""
Сервисы прикладного слоя для домена "Каталог".

Эти сервисы координируют работу между API и доменными сервисами,
обеспечивая преобразование данных и бизнес-логику прикладного уровня.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from decimal import Decimal

from database.repositories import AuthorRepository, CategoryRepository, AudiobookRepository
from database.services import CatalogDomainService
from schemas import (
    AudiobookSchema, AuthorSchema, CategorySchema, AudiobookListSchema,
    CreateAuthorRequest, CreateCategoryRequest, CreateAudiobookRequest,
    CreateAudiobookComprehensiveRequest, SearchAudiobooksRequest,
    CatalogStatisticsSchema, AuthorSummarySchema, CategoryAnalysisSchema
)


class CatalogApplicationService:
    """
    Сервис прикладного слоя для работы с каталогом аудиокниг.
    
    Координирует работу между API и доменными сервисами,
    обеспечивая преобразование данных и бизнес-логику прикладного уровня.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.author_repo = AuthorRepository(db)
        self.category_repo = CategoryRepository(db)
        self.audiobook_repo = AudiobookRepository(db)
        self.domain_service = CatalogDomainService(db)
    
    def get_all_audiobooks(
        self, 
        limit: Optional[int] = None, 
        offset: Optional[int] = None
    ) -> AudiobookListSchema:
        """
        Получить все аудиокниги с полной связанной информацией.
        
        Args:
            limit: Лимит записей
            offset: Смещение для пагинации
            
        Returns:
            Список аудиокниг с пагинацией
        """
        # Получаем аудиокниги с загруженными связями
        audiobooks = self.audiobook_repo.get_all(limit=limit, offset=offset)
        
        # Подсчитываем общее количество для пагинации
        total = self.audiobook_repo.get_all_count()
        
        # Преобразуем в DTO
        audiobook_schemas = [
            AudiobookSchema.model_validate(audiobook) 
            for audiobook in audiobooks
        ]
        
        # Определяем, есть ли еще записи
        has_more = False
        if limit and offset is not None:
            has_more = (offset + limit) < total
        
        return AudiobookListSchema(
            items=audiobook_schemas,
            total=total,
            limit=limit,
            offset=offset,
            has_more=has_more
        )
    
    def get_audiobook_by_id(self, audiobook_id: int) -> Optional[AudiobookSchema]:
        """
        Получить аудиокнигу по ID с полной связанной информацией.
        
        Args:
            audiobook_id: ID аудиокниги
            
        Returns:
            Аудиокнига с полной информацией или None
        """
        audiobook = self.audiobook_repo.get_by_id(audiobook_id)
        if not audiobook:
            return None
        
        return AudiobookSchema.model_validate(audiobook)
    
    def search_audiobooks(self, request: SearchAudiobooksRequest) -> AudiobookListSchema:
        """
        Поиск аудиокниг с множественными фильтрами.
        
        Args:
            request: Параметры поиска
            
        Returns:
            Список найденных аудиокниг
        """
        # Используем доменный сервис для комплексного поиска
        audiobooks = self.domain_service.search_audiobooks_comprehensive(
            query=request.query,
            author_id=request.author_id,
            category_ids=request.category_ids,
            min_price=float(request.min_price) if request.min_price else None,
            max_price=float(request.max_price) if request.max_price else None,
            limit=request.limit,
            offset=request.offset
        )
        
        # Подсчитываем общее количество для пагинации
        total = len(audiobooks)  # В реальном приложении нужен отдельный запрос для подсчета
        
        # Преобразуем в DTO
        audiobook_schemas = [
            AudiobookSchema.model_validate(audiobook) 
            for audiobook in audiobooks
        ]
        
        # Определяем, есть ли еще записи
        has_more = False
        if request.limit and request.offset is not None:
            has_more = (request.offset + request.limit) < total
        
        return AudiobookListSchema(
            items=audiobook_schemas,
            total=total,
            limit=request.limit,
            offset=request.offset,
            has_more=has_more
        )
    
    def create_audiobook(self, request: CreateAudiobookRequest) -> AudiobookSchema:
        """
        Создать аудиокнигу.
        
        Args:
            request: Данные для создания аудиокниги
            
        Returns:
            Созданная аудиокнига
        """
        # Создаем аудиокнигу
        audiobook = self.audiobook_repo.create(
            title=request.title,
            author_id=request.author_id,
            price=float(request.price),
            description=request.description,
            cover_image_url=request.cover_image_url
        )
        
        # Добавляем категории, если указаны
        if request.category_ids:
            for category_id in request.category_ids:
                self.audiobook_repo.add_category(audiobook.id, category_id)
        
        # Получаем полную информацию с загруженными связями
        full_audiobook = self.audiobook_repo.get_by_id(audiobook.id)
        
        return AudiobookSchema.model_validate(full_audiobook)
    
    def create_audiobook_comprehensive(
        self, 
        request: CreateAudiobookComprehensiveRequest
    ) -> AudiobookSchema:
        """
        Создать аудиокнигу с автоматическим созданием автора и категорий.
        
        Args:
            request: Данные для создания аудиокниги
            
        Returns:
            Созданная аудиокнига
        """
        # Используем доменный сервис для комплексного создания
        audiobook = self.domain_service.create_audiobook_with_author_and_categories(
            title=request.title,
            author_name=request.author_name,
            price=float(request.price),
            category_names=request.category_names,
            description=request.description,
            cover_image_url=request.cover_image_url
        )
        
        return AudiobookSchema.model_validate(audiobook)
    
    def get_all_authors(self) -> List[AuthorSchema]:
        """
        Получить всех авторов.
        
        Returns:
            Список авторов
        """
        authors = self.author_repo.get_all()
        return [AuthorSchema.model_validate(author) for author in authors]
    
    def get_author_by_id(self, author_id: int) -> Optional[AuthorSchema]:
        """
        Получить автора по ID.
        
        Args:
            author_id: ID автора
            
        Returns:
            Автор или None
        """
        author = self.author_repo.get_by_id(author_id)
        if not author:
            return None
        
        return AuthorSchema.model_validate(author)
    
    def create_author(self, request: CreateAuthorRequest) -> AuthorSchema:
        """
        Создать автора.
        
        Args:
            request: Данные для создания автора
            
        Returns:
            Созданный автор
        """
        author = self.author_repo.create(request.name)
        return AuthorSchema.model_validate(author)
    
    def get_all_categories(self) -> List[CategorySchema]:
        """
        Получить все категории.
        
        Returns:
            Список категорий
        """
        categories = self.category_repo.get_all()
        return [CategorySchema.model_validate(category) for category in categories]
    
    def get_category_by_id(self, category_id: int) -> Optional[CategorySchema]:
        """
        Получить категорию по ID.
        
        Args:
            category_id: ID категории
            
        Returns:
            Категория или None
        """
        category = self.category_repo.get_by_id(category_id)
        if not category:
            return None
        
        return CategorySchema.model_validate(category)
    
    def create_category(self, request: CreateCategoryRequest) -> CategorySchema:
        """
        Создать категорию.
        
        Args:
            request: Данные для создания категории
            
        Returns:
            Созданная категория
        """
        category = self.category_repo.create(request.name)
        return CategorySchema.model_validate(category)
    
    def get_audiobooks_by_author(self, author_id: int) -> List[AudiobookSchema]:
        """
        Получить аудиокниги по автору.
        
        Args:
            author_id: ID автора
            
        Returns:
            Список аудиокниг автора
        """
        audiobooks = self.audiobook_repo.get_by_author(author_id)
        return [AudiobookSchema.model_validate(ab) for ab in audiobooks]
    
    def get_audiobooks_by_category(self, category_id: int) -> List[AudiobookSchema]:
        """
        Получить аудиокниги по категории.
        
        Args:
            category_id: ID категории
            
        Returns:
            Список аудиокниг в категории
        """
        audiobooks = self.audiobook_repo.get_by_category(category_id)
        return [AudiobookSchema.model_validate(ab) for ab in audiobooks]
    
    def get_catalog_statistics(self) -> CatalogStatisticsSchema:
        """
        Получить статистику каталога.
        
        Returns:
            Статистика каталога
        """
        stats = self.domain_service.get_catalog_statistics()
        return CatalogStatisticsSchema.model_validate(stats)
    
    def get_author_summary(self, author_id: int) -> Optional[AuthorSummarySchema]:
        """
        Получить сводку работ автора.
        
        Args:
            author_id: ID автора
            
        Returns:
            Сводка работ автора или None
        """
        summary = self.domain_service.get_author_works_summary(author_id)
        if not summary:
            return None
        
        return AuthorSummarySchema.model_validate(summary)
    
    def get_category_analysis(self, category_id: int) -> Optional[CategoryAnalysisSchema]:
        """
        Получить анализ категории.
        
        Args:
            category_id: ID категории
            
        Returns:
            Анализ категории или None
        """
        analysis = self.domain_service.get_category_analysis(category_id)
        if not analysis:
            return None
        
        return CategoryAnalysisSchema.model_validate(analysis) 