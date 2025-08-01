from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from decimal import Decimal


class CartItemInput(BaseModel):
    """Схема для входного элемента корзины"""
    audiobook_id: int = Field(..., description="ID аудиокниги")
    quantity: int = Field(..., gt=0, description="Количество")


class OrderCreateRequest(BaseModel):
    """Схема для создания заказа"""
    items: List[CartItemInput] = Field(..., description="Список товаров в корзине")


class OrderItemResponse(BaseModel):
    """Схема для ответа с позицией заказа"""
    id: int
    audiobook_id: int
    title: str
    price_per_unit: Decimal
    quantity: int
    total_price: Decimal
    created_at: datetime

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    """Схема для ответа с заказом"""
    id: int
    order_number: str
    total_amount: Decimal
    status: str
    items: List[OrderItemResponse]
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CartCalculationResponse(BaseModel):
    """Схема для ответа от сервиса корзины"""
    items: List[dict]
    total_price: float
    calculated_at: datetime


class ErrorResponse(BaseModel):
    """Схема для ответа с ошибкой"""
    error: str
    detail: Optional[str] = None 