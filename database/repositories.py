from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any
from .models import Base, Author, Category, Audiobook


class AuthorRepository:
    """
    Репозиторий для работы с сущностью Author.
    
    В контексте DDD репозиторий инкапсулирует логику доступа к данным
    и предоставляет интерфейс для работы с агрегатами.
    """
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, name: str) -> Author:
        """
        Создает нового автора.
        
        Args:
            name: Имя автора
            
        Returns:
            Созданный объект Author
        """
        author = Author(name=name)
        self.session.add(author)
        self.session.commit()
        return author
    
    def get_by_id(self, author_id: int) -> Optional[Author]:
        """
        Получает автора по ID.
        
        Args:
            author_id: ID автора
            
        Returns:
            Объект Author или None
        """
        return self.session.query(Author).filter(Author.id == author_id).first()
    
    def get_by_name(self, name: str) -> Optional[Author]:
        """
        Получает автора по имени.
        
        Args:
            name: Имя автора
            
        Returns:
            Объект Author или None
        """
        return self.session.query(Author).filter(Author.name == name).first()
    
    def get_all(self) -> List[Author]:
        """
        Получает всех авторов.
        
        Returns:
            Список всех авторов
        """
        return self.session.query(Author).all()
    
    def update(self, author_id: int, name: str) -> Optional[Author]:
        """
        Обновляет автора.
        
        Args:
            author_id: ID автора
            name: Новое имя
            
        Returns:
            Обновленный объект Author или None
        """
        author = self.get_by_id(author_id)
        if author:
            author.name = name
            self.session.commit()
        return author
    
    def delete(self, author_id: int) -> bool:
        """
        Удаляет автора.
        
        Args:
            author_id: ID автора
            
        Returns:
            True если автор был удален, False если не найден
        """
        author = self.get_by_id(author_id)
        if author:
            self.session.delete(author)
            self.session.commit()
            return True
        return False


class CategoryRepository:
    """
    Репозиторий для работы с сущностью Category.
    """
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, name: str) -> Category:
        """
        Создает новую категорию.
        
        Args:
            name: Название категории
            
        Returns:
            Созданный объект Category
        """
        category = Category(name=name)
        self.session.add(category)
        self.session.commit()
        return category
    
    def get_by_id(self, category_id: int) -> Optional[Category]:
        """
        Получает категорию по ID.
        
        Args:
            category_id: ID категории
            
        Returns:
            Объект Category или None
        """
        return self.session.query(Category).filter(Category.id == category_id).first()
    
    def get_by_name(self, name: str) -> Optional[Category]:
        """
        Получает категорию по названию.
        
        Args:
            name: Название категории
            
        Returns:
            Объект Category или None
        """
        return self.session.query(Category).filter(Category.name == name).first()
    
    def get_all(self) -> List[Category]:
        """
        Получает все категории.
        
        Returns:
            Список всех категорий
        """
        return self.session.query(Category).all()
    
    def update(self, category_id: int, name: str) -> Optional[Category]:
        """
        Обновляет категорию.
        
        Args:
            category_id: ID категории
            name: Новое название
            
        Returns:
            Обновленный объект Category или None
        """
        category = self.get_by_id(category_id)
        if category:
            category.name = name
            self.session.commit()
        return category
    
    def delete(self, category_id: int) -> bool:
        """
        Удаляет категорию.
        
        Args:
            category_id: ID категории
            
        Returns:
            True если категория была удалена, False если не найдена
        """
        category = self.get_by_id(category_id)
        if category:
            self.session.delete(category)
            self.session.commit()
            return True
        return False


class AudiobookRepository:
    """
    Репозиторий для работы с агрегатом Audiobook.
    
    В контексте DDD это основной репозиторий, который работает с корнем агрегата
    и обеспечивает целостность данных.
    """
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, title: str, author_id: int, price: float, 
               description: str = None, cover_image_url: str = None) -> Audiobook:
        """
        Создает новую аудиокнигу.
        
        Args:
            title: Название аудиокниги
            author_id: ID автора
            price: Цена
            description: Описание
            cover_image_url: URL обложки
            
        Returns:
            Созданный объект Audiobook
        """
        audiobook = Audiobook(
            title=title,
            author_id=author_id,
            price=price,
            description=description,
            cover_image_url=cover_image_url
        )
        self.session.add(audiobook)
        self.session.commit()
        return audiobook
    
    def get_by_id(self, audiobook_id: int) -> Optional[Audiobook]:
        """
        Получает аудиокнигу по ID с загруженными связями.
        
        Args:
            audiobook_id: ID аудиокниги
            
        Returns:
            Объект Audiobook или None
        """
        return self.session.query(Audiobook).options(
            joinedload(Audiobook.author),
            joinedload(Audiobook.categories)
        ).filter(Audiobook.id == audiobook_id).first()
    
    def get_by_ids(self, audiobook_ids: List[int]) -> List[Audiobook]:
        """
        Получает аудиокниги по списку ID.
        
        Args:
            audiobook_ids: Список ID аудиокниг
            
        Returns:
            Список объектов Audiobook
        """
        if not audiobook_ids:
            return []
        return self.session.query(Audiobook).options(
            joinedload(Audiobook.author),
            joinedload(Audiobook.categories)
        ).filter(Audiobook.id.in_(audiobook_ids)).all()
    
    def get_all(self, limit: int = None, offset: int = None) -> List[Audiobook]:
        """
        Получает все аудиокниги с пагинацией.
        
        Args:
            limit: Лимит записей
            offset: Смещение
            
        Returns:
            Список аудиокниг
        """
        query = self.session.query(Audiobook).options(
            joinedload(Audiobook.author),
            joinedload(Audiobook.categories)
        )
        
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
            
        return query.all()
    
    def get_all_count(self) -> int:
        """
        Получить общее количество аудиокниг.
        
        Returns:
            Общее количество аудиокниг
        """
        return self.session.query(Audiobook).count()
    
    def get_by_author(self, author_id: int) -> List[Audiobook]:
        """
        Получает аудиокниги по автору.
        
        Args:
            author_id: ID автора
            
        Returns:
            Список аудиокниг автора
        """
        return self.session.query(Audiobook).options(
            joinedload(Audiobook.author),
            joinedload(Audiobook.categories)
        ).filter(Audiobook.author_id == author_id).all()
    
    def get_by_category(self, category_id: int) -> List[Audiobook]:
        """
        Получает аудиокниги по категории.
        
        Args:
            category_id: ID категории
            
        Returns:
            Список аудиокниг в категории
        """
        return self.session.query(Audiobook).options(
            joinedload(Audiobook.author),
            joinedload(Audiobook.categories)
        ).join(Audiobook.categories).filter(Category.id == category_id).all()
    
    def search(self, query: str, limit: Optional[int] = None) -> List[Audiobook]:
        """
        Поиск аудиокниг по названию, автору или описанию.
        
        Args:
            query: Поисковый запрос
            limit: Максимальное количество результатов
            
        Returns:
            Список найденных аудиокниг
        """
        query_obj = self.session.query(Audiobook).options(
            joinedload(Audiobook.author),
            joinedload(Audiobook.categories)
        ).filter(
            or_(
                Audiobook.title.ilike(f"%{query}%"),
                Audiobook.description.ilike(f"%{query}%"),
                Author.name.ilike(f"%{query}%")
            )
        )
        
        if limit:
            query_obj = query_obj.limit(limit)
            
        return query_obj.all()
    
    def update(self, audiobook_id: int, **kwargs) -> Optional[Audiobook]:
        """
        Обновляет аудиокнигу.
        
        Args:
            audiobook_id: ID аудиокниги
            **kwargs: Поля для обновления
            
        Returns:
            Обновленный объект Audiobook или None
        """
        audiobook = self.get_by_id(audiobook_id)
        if audiobook:
            for key, value in kwargs.items():
                if hasattr(audiobook, key):
                    setattr(audiobook, key, value)
            self.session.commit()
        return audiobook
    
    def delete(self, audiobook_id: int) -> bool:
        """
        Удаляет аудиокнигу.
        
        Args:
            audiobook_id: ID аудиокниги
            
        Returns:
            True если аудиокнига была удалена, False если не найдена
        """
        audiobook = self.get_by_id(audiobook_id)
        if audiobook:
            self.session.delete(audiobook)
            self.session.commit()
            return True
        return False
    
    def add_category(self, audiobook_id: int, category_id: int) -> bool:
        """
        Добавляет категорию к аудиокниге.
        
        Args:
            audiobook_id: ID аудиокниги
            category_id: ID категории
            
        Returns:
            True если категория была добавлена
        """
        audiobook = self.get_by_id(audiobook_id)
        category = self.session.query(Category).filter(Category.id == category_id).first()
        
        if audiobook and category:
            audiobook.add_category(category)
            self.session.commit()
            return True
        return False
    
    def remove_category(self, audiobook_id: int, category_id: int) -> bool:
        """
        Удаляет категорию из аудиокниги.
        
        Args:
            audiobook_id: ID аудиокниги
            category_id: ID категории
            
        Returns:
            True если категория была удалена
        """
        audiobook = self.get_by_id(audiobook_id)
        category = self.session.query(Category).filter(Category.id == category_id).first()
        
        if audiobook and category:
            audiobook.remove_category(category)
            self.session.commit()
            return True
        return False 