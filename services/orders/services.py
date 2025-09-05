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
from schemas import OrderCreateRequest, CartCalculationResponse


class OrderService:
    """Сервис для работы с заказами"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def generate_order_number(self) -> str:
        """
        Генерирует уникальный номер заказа.
        
        Returns:
            Уникальный номер заказа
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"ORD-{timestamp}-{unique_id}"
    
    async def validate_cart_with_cart_service(self, cart_items: List[dict]) -> CartCalculationResponse:
        """
        Валидирует корзину через микросервис корзины.
        
        Args:
            cart_items: Список товаров в корзине
            
        Returns:
            Валидированная информация о корзине
            
        Raises:
            HTTPException: Если сервис корзины недоступен или вернул ошибку
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    "http://localhost:8004/api/v1/cart/calculate",
                    json={"items": cart_items}
                )
                
                if response.status_code == 200:
                    return CartCalculationResponse(**response.json())
                else:
                    raise httpx.HTTPStatusError(
                        f"Сервис корзины вернул ошибку: {response.status_code}",
                        request=response.request,
                        response=response
                    )
                    
        except httpx.RequestError as e:
            raise httpx.HTTPStatusError(
                f"Не удалось подключиться к сервису корзины: {str(e)}",
                request=None,
                response=None
            )
    
    def create_order_transaction(self, cart_response: CartCalculationResponse) -> Order:
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
                    audiobook_id=item['audiobook_id'],
                    title=item['title'],
                    price_per_unit=item['price_per_unit'],
                    quantity=item['quantity']
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