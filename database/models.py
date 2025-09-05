from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from typing import List, Optional
import uuid

Base = declarative_base()

# Таблица связи многие-ко-многим между Audiobook и Category
audiobook_category = Table(
    'audiobook_category',
    Base.metadata,
    Column('audiobook_id', Integer, ForeignKey('audiobooks.id'), primary_key=True),
    Column('category_id', Integer, ForeignKey('categories.id'), primary_key=True)
)


class User(Base):
    """
    Сущность User (Пользователь) - представляет пользователя системы.
    
    В контексте DDD это является сущностью, которая может существовать независимо
    и имеет свой собственный жизненный цикл.
    """
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    
    # Метаданные
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"
    
    def __str__(self):
        return self.email


class Author(Base):
    """
    Сущность Author (Автор) - представляет автора аудиокниг.
    
    В контексте DDD это является сущностью, которая может существовать независимо
    и имеет свой собственный жизненный цикл.
    """
    __tablename__ = 'authors'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связь один-ко-многим с Audiobook
    audiobooks = relationship("Audiobook", back_populates="author", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Author(id={self.id}, name='{self.name}')>"
    
    def __str__(self):
        return self.name


class Category(Base):
    """
    Сущность Category (Категория) - представляет категорию/жанр аудиокниг.
    
    В контексте DDD это является сущностью, которая может существовать независимо
    и имеет свой собственный жизненный цикл.
    """
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связь многие-ко-многим с Audiobook
    audiobooks = relationship("Audiobook", secondary=audiobook_category, back_populates="categories")
    
    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"
    
    def __str__(self):
        return self.name


class Audiobook(Base):
    """
    Агрегат Audiobook (Аудиокнига) - корневая сущность агрегата.
    
    В контексте DDD это является корнем агрегата, который инкапсулирует
    бизнес-логику и обеспечивает целостность данных.
    """
    __tablename__ = 'audiobooks'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    cover_image_url = Column(String(500), nullable=True)
    
    # Внешний ключ к Author (связь один-ко-многим)
    author_id = Column(Integer, ForeignKey('authors.id'), nullable=False)
    
    # Метаданные
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    author = relationship("Author", back_populates="audiobooks")
    categories = relationship("Category", secondary=audiobook_category, back_populates="audiobooks")
    
    def __repr__(self):
        return f"<Audiobook(id={self.id}, title='{self.title}', author_id={self.author_id})>"
    
    def __str__(self):
        return f"{self.title} by {self.author.name if self.author else 'Unknown Author'}"
    
    # Бизнес-методы агрегата
    def add_category(self, category: Category) -> None:
        """
        Добавляет категорию к аудиокниге.
        
        Args:
            category: Категория для добавления
        """
        if category not in self.categories:
            self.categories.append(category)
    
    def remove_category(self, category: Category) -> None:
        """
        Удаляет категорию из аудиокниги.
        
        Args:
            category: Категория для удаления
        """
        if category in self.categories:
            self.categories.remove(category)
    
    def update_price(self, new_price: float) -> None:
        """
        Обновляет цену аудиокниги.
        
        Args:
            new_price: Новая цена
        """
        if new_price < 0:
            raise ValueError("Цена не может быть отрицательной")
        self.price = new_price
    
    def get_categories_names(self) -> List[str]:
        """
        Возвращает список названий категорий аудиокниги.
        
        Returns:
            Список названий категорий
        """
        return [category.name for category in self.categories]
    
    def has_category(self, category_name: str) -> bool:
        """
        Проверяет, принадлежит ли аудиокнига к указанной категории.
        
        Args:
            category_name: Название категории для проверки
            
        Returns:
            True, если аудиокнига принадлежит к категории
        """
        return any(category.name == category_name for category in self.categories)
    
    @property
    def author_name(self) -> str:
        """
        Возвращает имя автора аудиокниги.
        
        Returns:
            Имя автора или "Unknown Author" если автор не установлен
        """
        return self.author.name if self.author else "Unknown Author"


class Order(Base):
    """
    Агрегат Order (Заказ) - корневая сущность агрегата заказа.
    
    В контексте DDD это является корнем агрегата, который инкапсулирует
    бизнес-логику заказа и обеспечивает целостность данных.
    """
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_number = Column(String(50), nullable=False, unique=True, index=True)
    total_amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(50), nullable=False, default='pending')
    
    # Метаданные
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Order(id={self.id}, order_number='{self.order_number}', total_amount={self.total_amount})>"
    
    def __str__(self):
        return f"Заказ #{self.order_number} на сумму {self.total_amount}"
    
    # Бизнес-методы агрегата
    def add_item(self, audiobook_id: int, title: str, price_per_unit: float, quantity: int) -> None:
        """
        Добавляет товар в заказ.
        
        Args:
            audiobook_id: ID аудиокниги
            title: Название аудиокниги
            price_per_unit: Цена за единицу
            quantity: Количество
        """
        item = OrderItem(
            order_id=self.id,
            audiobook_id=audiobook_id,
            title=title,
            price_per_unit=price_per_unit,
            quantity=quantity
        )
        self.items.append(item)
        self._recalculate_total()
    
    def _recalculate_total(self) -> None:
        """
        Пересчитывает общую сумму заказа.
        """
        self.total_amount = sum(item.total_price for item in self.items)
    
    def update_status(self, new_status: str) -> None:
        """
        Обновляет статус заказа.
        
        Args:
            new_status: Новый статус заказа
        """
        valid_statuses = ['pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled']
        if new_status not in valid_statuses:
            raise ValueError(f"Неверный статус заказа. Допустимые значения: {valid_statuses}")
        self.status = new_status
    
    def get_items_count(self) -> int:
        """
        Возвращает количество товаров в заказе.
        
        Returns:
            Количество товаров
        """
        return len(self.items)
    
    def get_total_items_quantity(self) -> int:
        """
        Возвращает общее количество единиц товаров в заказе.
        
        Returns:
            Общее количество единиц
        """
        return sum(item.quantity for item in self.items)


class OrderItem(Base):
    """
    Сущность OrderItem (Позиция заказа) - представляет товар в заказе.
    
    В контексте DDD это является частью агрегата Order и не может существовать
    независимо от заказа.
    """
    __tablename__ = 'order_items'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Внешний ключ к Order
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    
    # Информация о товаре (фиксируется на момент покупки)
    audiobook_id = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    price_per_unit = Column(Numeric(10, 2), nullable=False)
    quantity = Column(Integer, nullable=False)
    
    # Метаданные
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    order = relationship("Order", back_populates="items")
    
    @property
    def total_price(self) -> float:
        """
        Возвращает общую стоимость позиции.
        
        Returns:
            Общая стоимость позиции
        """
        return float(self.price_per_unit * self.quantity)
    
    def __repr__(self):
        return f"<OrderItem(id={self.id}, audiobook_id={self.audiobook_id}, title='{self.title}', quantity={self.quantity})>"
    
    def __str__(self):
        return f"{self.title} x {self.quantity} = {self.total_price}"
