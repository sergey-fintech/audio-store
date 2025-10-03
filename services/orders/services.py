import sys
import os

# Добавляем корневую директорию проекта в путь Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import httpx
import asyncio
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import uuid

from database.models import Order, OrderItem
from services.orders.schemas import OrderCreateRequest, CartCalculationResponse
from services.shared_services.cart import CartService, CartItemInput, CartCalculationResult


class OrderService:
    """Сервис для работы с заказами"""
    
    def __init__(self, db_session: Session, cart_service: CartService):
        self.db = db_session
        self.cart_service = cart_service
    
    def generate_order_number(self) -> str:
        """
        Генерирует уникальный номер заказа.
        
        Returns:
            Уникальный номер заказа
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"ORD-{timestamp}-{unique_id}"
    
    def validate_cart(self, cart_items: List[CartItemInput]) -> CartCalculationResult:
        """
        Валидирует корзину через CartService.
        
        Args:
            cart_items: Список товаров в корзине
            
        Returns:
            Валидированная информация о корзине
        """
        return self.cart_service.calculate_cart(cart_items)
    
    def create_order_transaction(self, cart_response: CartCalculationResult) -> Order:
        """
        Создает заказ в транзакции.
        
        Args:
            cart_response: Ответ от сервиса корзины
            
        Returns:
            Созданный заказ
            
        Raises:
            SQLAlchemyError: При ошибке базы данных
        """
        try:
            # Создаем заказ
            order = Order(
                order_number=self.generate_order_number(),
                total_amount=cart_response.total_price,
                status='pending'
            )
            
            self.db.add(order)
            self.db.flush()  # Получаем ID заказа
            
            # Создаем позиции заказа
            for item in cart_response.items:
                order_item = OrderItem(
                    order_id=order.id,
                    audiobook_id=item.audiobook_id,
                    title=item.title,
                    price_per_unit=item.price_per_unit,
                    quantity=item.quantity
                )
                self.db.add(order_item)
            
            self.db.commit()
            return order
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e
    
    def get_order_by_id(self, order_id: int) -> Optional[Order]:
        """
        Получает заказ по ID.
        
        Args:
            order_id: ID заказа
            
        Returns:
            Заказ или None, если не найден
        """
        return self.db.query(Order).filter(Order.id == order_id).first()
    
    def get_order_by_number(self, order_number: str) -> Optional[Order]:
        """
        Получает заказ по номеру.
        
        Args:
            order_number: Номер заказа
            
        Returns:
            Заказ или None, если не найден
        """
        return self.db.query(Order).filter(Order.order_number == order_number).first()
    
    def get_all_orders(self, limit: int = 100, offset: int = 0) -> List[Order]:
        """
        Получает список всех заказов.
        
        Args:
            limit: Максимальное количество заказов
            offset: Смещение
            
        Returns:
            Список заказов
        """
        return self.db.query(Order).order_by(Order.created_at.desc()).limit(limit).offset(offset).all()
    
    def update_order_status(self, order_id: int, new_status: str) -> Optional[Order]:
        """
        Обновляет статус заказа.
        
        Args:
            order_id: ID заказа
            new_status: Новый статус
            
        Returns:
            Обновленный заказ или None, если не найден
        """
        order = self.get_order_by_id(order_id)
        if order:
            order.update_status(new_status)
            self.db.commit()
        return order 