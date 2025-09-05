# Этот сервис отвечает за управление заказами и корзиной покупок, включая:
# - Корзину покупок (добавление, удаление, изменение количества товаров)
# - Создание и обработку заказов
# - Расчет стоимости и применение скидок
# - Историю заказов пользователя
# - Статусы заказов и отслеживание
# - Интеграцию с платежными системами
# - Уведомления о статусе заказов

import sys
import os

# Добавляем корневую директорию проекта в путь Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import httpx
from contextlib import asynccontextmanager

from database.connection import get_db
from database.models import Order, OrderItem
from schemas import (
    OrderCreateRequest, 
    OrderResponse, 
    OrderItemResponse, 
    ErrorResponse,
    CartCalculationResponse
)
from services import OrderService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Инициализация при запуске
    print("🚀 Микросервис 'Заказы' запускается...")
    yield
    # Очистка при завершении
    print("🛑 Микросервис 'Заказы' завершает работу...")


app = FastAPI(
    title="Микросервис Заказы",
    description="Микросервис для создания и управления заказами",
    version="1.0.0",
    lifespan=lifespan
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Корневой эндпоинт для проверки работы сервиса"""
    return {
        "message": "Микросервис 'Заказы' работает",
        "version": "1.0.0",
        "endpoints": {
            "create_order": "POST /api/v1/orders",
            "get_order": "GET /api/v1/orders/{order_id}",
            "get_orders": "GET /api/v1/orders",
            "health": "GET /health"
        }
    }


@app.get("/health")
async def health_check():
    """Эндпоинт для проверки состояния сервиса"""
    return {
        "status": "healthy",
        "service": "orders",
        "timestamp": "2024-01-01T00:00:00Z"
    }


@app.post("/api/v1/orders", response_model=OrderResponse)
async def create_order(
    request: OrderCreateRequest,
    db: Session = Depends(get_db)
):
    """
    Создает новый заказ.
    
    Процесс создания заказа:
    1. Принимает "сырой" состав корзины (список ID аудиокниг и их количество)
    2. Обращается к микросервису "Корзина" для валидации и расчета стоимости
    3. Транзакционно создает заказ и позиции заказа
    4. Возвращает информацию о созданном заказе
    """
    try:
        # Создаем сервис для работы с заказами
        order_service = OrderService(db)
        
        # Подготавливаем данные для отправки в сервис корзины
        cart_items = [
            {
                "audiobook_id": item.audiobook_id,
                "quantity": item.quantity
            }
            for item in request.items
        ]
        
        # Валидируем корзину через микросервис корзины
        try:
            cart_response = await order_service.validate_cart_with_cart_service(cart_items)
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Сервис корзины недоступен: {str(e)}"
            )
        
        # Проверяем, что корзина не пустая
        if not cart_response.items:
            raise HTTPException(
                status_code=400,
                detail="Корзина пуста или содержит недействительные товары"
            )
        
        # Создаем заказ в транзакции
        try:
            order = order_service.create_order_transaction(cart_response)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Ошибка при создании заказа: {str(e)}"
            )
        
        # Возвращаем информацию о созданном заказе
        return OrderResponse(
            id=order.id,
            order_number=order.order_number,
            total_amount=order.total_amount,
            status=order.status,
            items=[
                OrderItemResponse(
                    id=item.id,
                    audiobook_id=item.audiobook_id,
                    title=item.title,
                    price_per_unit=item.price_per_unit,
                    quantity=item.quantity,
                    total_price=item.total_price,
                    created_at=item.created_at
                )
                for item in order.items
            ],
            created_at=order.created_at,
            updated_at=order.updated_at
        )
        
    except HTTPException:
        # Перебрасываем HTTP исключения как есть
        raise
    except Exception as e:
        # Логируем неожиданные ошибки
        print(f"Неожиданная ошибка при создании заказа: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Внутренняя ошибка сервера"
        )


@app.get("/api/v1/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, db: Session = Depends(get_db)):
    """Получает заказ по ID"""
    order_service = OrderService(db)
    order = order_service.get_order_by_id(order_id)
    
    if not order:
        raise HTTPException(
            status_code=404,
            detail=f"Заказ с ID {order_id} не найден"
        )
    
    return OrderResponse(
        id=order.id,
        order_number=order.order_number,
        total_amount=order.total_amount,
        status=order.status,
        items=[
            OrderItemResponse(
                id=item.id,
                audiobook_id=item.audiobook_id,
                title=item.title,
                price_per_unit=item.price_per_unit,
                quantity=item.quantity,
                total_price=item.total_price,
                created_at=item.created_at
            )
            for item in order.items
        ],
        created_at=order.created_at,
        updated_at=order.updated_at
    )


@app.get("/api/v1/orders", response_model=list[OrderResponse])
async def get_orders(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Получает список всех заказов"""
    order_service = OrderService(db)
    orders = order_service.get_all_orders(limit=limit, offset=offset)
    
    return [
        OrderResponse(
            id=order.id,
            order_number=order.order_number,
            total_amount=order.total_amount,
            status=order.status,
            items=[
                OrderItemResponse(
                    id=item.id,
                    audiobook_id=item.audiobook_id,
                    title=item.title,
                    price_per_unit=item.price_per_unit,
                    quantity=item.quantity,
                    total_price=item.total_price,
                    created_at=item.created_at
                )
                for item in order.items
            ],
            created_at=order.created_at,
            updated_at=order.updated_at
        )
        for order in orders
    ]


@app.put("/api/v1/orders/{order_id}/status")
async def update_order_status(
    order_id: int,
    status: str,
    db: Session = Depends(get_db)
):
    """Обновляет статус заказа"""
    order_service = OrderService(db)
    order = order_service.update_order_status(order_id, status)
    
    if not order:
        raise HTTPException(
            status_code=404,
            detail=f"Заказ с ID {order_id} не найден"
        )
    
    return {
        "message": f"Статус заказа {order_id} обновлен на '{status}'",
        "order_id": order_id,
        "new_status": status
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
