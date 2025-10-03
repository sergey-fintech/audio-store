from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from datetime import datetime

import sys
from pathlib import Path

# Добавляем путь к корневой директории проекта
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from services.shared_services.cart import CartService, get_cart_service, CartItemInput, CartCalculationResult

app = FastAPI(
    title="Корзина API",
    description="Микросервис для валидации и расчета стоимости корзины",
    version="1.0.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене замените на конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CartCalculationRequest(BaseModel):
    items: List[CartItemInput]

@app.post("/api/v1/cart/calculate", response_model=CartCalculationResult)
def calculate_cart(request: CartCalculationRequest, cart_service: CartService = Depends(get_cart_service)):
    """
    Рассчитывает стоимость корзины на основе списка товаров,
    используя прямой вызов CartService.
    """
    return cart_service.calculate_cart(request.items)

@app.get("/health")
async def health_check():
    """
    Эндпоинт для проверки состояния сервиса
    """
    return {"status": "healthy", "service": "cart"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
