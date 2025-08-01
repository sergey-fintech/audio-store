from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from .models import Author, Category, Audiobook
from .repositories import AuthorRepository, CategoryRepository, AudiobookRepository


class CatalogDomainService:
    """
    Доменный сервис для каталога аудиокниг.
    
    В контексте DDD доменные сервисы содержат бизнес-логику, которая
    не принадлежит конкретному агрегату, а работает с несколькими агрегатами.
    """
    
    def __init__(self, session: Session):
        self.session = session
        self.author_repo = AuthorRepository(session)
        self.category_repo = CategoryRepository(session)
        self.audiobook_repo = AudiobookRepository(session)
    
    def create_audiobook_with_author_and_categories(
        self, 
        title: str, 
        author_name: str, 
        price: float,
        category_names: List[str] = None,
        description: str = None,
        cover_image_url: str = None
    ) -> Audiobook:
        """
        Создает аудиокнигу с автором и категориями.
        
        Этот метод инкапсулирует сложную бизнес-логику создания аудиокниги,
        включая создание или поиск автора и категорий.
        
        Args:
            title: Название аудиокниги
            author_name: Имя автора
            price: Цена
            category_names: Список названий категорий
            description: Описание
            cover_image_url: URL обложки
            
        Returns:
            Созданная аудиокнига
        """
        # Найти или создать автора
        author = self.author_repo.get_by_name(author_name)
        if not author:
            author = self.author_repo.create(author_name)
        
        # Создать аудиокнигу
        audiobook = self.audiobook_repo.create(
            title=title,
            author_id=author.id,
            price=price,
            description=description,
            cover_image_url=cover_image_url
        )
        
        # Добавить категории
        if category_names:
            for category_name in category_names:
                category = self.category_repo.get_by_name(category_name)
                if not category:
                    category = self.category_repo.create(category_name)
                
                audiobook.add_category(category)
        
        self.session.commit()
        return audiobook
    
    def get_catalog_statistics(self) -> Dict[str, Any]:
        """
        Получает статистику каталога.
        
        Returns:
            Словарь со статистикой
        """
        total_authors = self.session.query(Author).count()
        total_categories = self.session.query(Category).count()
        total_audiobooks = self.session.query(Audiobook).count()
        
        # Средняя цена аудиокниг
        avg_price = self.session.query(Audiobook.price).scalar()
        if avg_price is None:
            avg_price = 0.0
        
        # Количество аудиокниг по категориям
        category_stats = self.session.query(
            Category.name,
            self.session.func.count(Audiobook.id).label('count')
        ).join(Category.audiobooks).group_by(Category.name).all()
        
        return {
            'total_authors': total_authors,
            'total_categories': total_categories,
            'total_audiobooks': total_audiobooks,
            'average_price': float(avg_price),
            'category_distribution': [
                {'category': name, 'count': count} 
                for name, count in category_stats
            ]
        }
    
    def search_audiobooks_comprehensive(
        self, 
        query: str = None,
        author_id: int = None,
        category_ids: List[int] = None,
        min_price: float = None,
        max_price: float = None,
        limit: int = None,
        offset: int = None
    ) -> List[Audiobook]:
        """
        Комплексный поиск аудиокниг с множественными фильтрами.
        
        Args:
            query: Поисковый запрос по названию и описанию
            author_id: ID автора для фильтрации
            category_ids: Список ID категорий для фильтрации
            min_price: Минимальная цена
            max_price: Максимальная цена
            limit: Лимит результатов
            offset: Смещение результатов
            
        Returns:
            Список найденных аудиокниг
        """
        query_builder = self.session.query(Audiobook).options(
            self.session.joinedload(Audiobook.author),
            self.session.joinedload(Audiobook.categories)
        )
        
        # Фильтр по поисковому запросу
        if query:
            query_builder = query_builder.filter(
                self.session.or_(
                    Audiobook.title.ilike(f"%{query}%"),
                    Audiobook.description.ilike(f"%{query}%")
                )
            )
        
        # Фильтр по автору
        if author_id:
            query_builder = query_builder.filter(Audiobook.author_id == author_id)
        
        # Фильтр по категориям
        if category_ids:
            query_builder = query_builder.join(Audiobook.categories).filter(
                Category.id.in_(category_ids)
            )
        
        # Фильтр по цене
        if min_price is not None:
            query_builder = query_builder.filter(Audiobook.price >= min_price)
        
        if max_price is not None:
            query_builder = query_builder.filter(Audiobook.price <= max_price)
        
        # Пагинация
        if offset:
            query_builder = query_builder.offset(offset)
        if limit:
            query_builder = query_builder.limit(limit)
        
        return query_builder.all()
    
    def get_author_works_summary(self, author_id: int) -> Dict[str, Any]:
        """
        Получает сводку работ автора.
        
        Args:
            author_id: ID автора
            
        Returns:
            Словарь со сводкой работ автора
        """
        author = self.author_repo.get_by_id(author_id)
        if not author:
            return None
        
        audiobooks = self.audiobook_repo.get_by_author(author_id)
        
        # Статистика по категориям
        category_counts = {}
        total_price = 0
        
        for audiobook in audiobooks:
            total_price += float(audiobook.price)
            for category in audiobook.categories:
                category_counts[category.name] = category_counts.get(category.name, 0) + 1
        
        return {
            'author': {
                'id': author.id,
                'name': author.name
            },
            'total_works': len(audiobooks),
            'total_value': total_price,
            'average_price': total_price / len(audiobooks) if audiobooks else 0,
            'category_distribution': category_counts,
            'audiobooks': [
                {
                    'id': ab.id,
                    'title': ab.title,
                    'price': float(ab.price),
                    'categories': [cat.name for cat in ab.categories]
                }
                for ab in audiobooks
            ]
        }
    
    def get_category_analysis(self, category_id: int) -> Dict[str, Any]:
        """
        Получает анализ категории.
        
        Args:
            category_id: ID категории
            
        Returns:
            Словарь с анализом категории
        """
        category = self.category_repo.get_by_id(category_id)
        if not category:
            return None
        
        audiobooks = self.audiobook_repo.get_by_category(category_id)
        
        # Статистика
        total_price = sum(float(ab.price) for ab in audiobooks)
        author_counts = {}
        
        for audiobook in audiobooks:
            author_name = audiobook.author.name
            author_counts[author_name] = author_counts.get(author_name, 0) + 1
        
        return {
            'category': {
                'id': category.id,
                'name': category.name
            },
            'total_audiobooks': len(audiobooks),
            'total_value': total_price,
            'average_price': total_price / len(audiobooks) if audiobooks else 0,
            'top_authors': sorted(
                author_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5],
            'audiobooks': [
                {
                    'id': ab.id,
                    'title': ab.title,
                    'author': ab.author.name,
                    'price': float(ab.price)
                }
                for ab in audiobooks
            ]
        }
    
    def validate_audiobook_data(
        self, 
        title: str, 
        author_id: int, 
        price: float,
        category_ids: List[int] = None
    ) -> Dict[str, Any]:
        """
        Валидирует данные аудиокниги.
        
        Args:
            title: Название аудиокниги
            author_id: ID автора
            price: Цена
            category_ids: Список ID категорий
            
        Returns:
            Словарь с результатами валидации
        """
        errors = []
        warnings = []
        
        # Проверка названия
        if not title or len(title.strip()) == 0:
            errors.append("Название аудиокниги не может быть пустым")
        elif len(title) > 255:
            errors.append("Название аудиокниги слишком длинное")
        
        # Проверка автора
        author = self.author_repo.get_by_id(author_id)
        if not author:
            errors.append("Указанный автор не существует")
        
        # Проверка цены
        if price < 0:
            errors.append("Цена не может быть отрицательной")
        elif price > 10000:
            warnings.append("Цена кажется слишком высокой")
        
        # Проверка категорий
        if category_ids:
            for category_id in category_ids:
                category = self.category_repo.get_by_id(category_id)
                if not category:
                    errors.append(f"Категория с ID {category_id} не существует")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        } 