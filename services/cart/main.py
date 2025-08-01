from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import httpx
import asyncio
from datetime import datetime

app = FastAPI(
    title="Корзина API",
    description="Микросервис для валидации и расчета стоимости корзины",
    version="1.0.0"
)

# DTO модели для входных и выходных данных
class CartItemInput(BaseModel):
    audiobook_id: int
    quantity: int

class CartItemOutput(BaseModel):
    audiobook_id: int
    title: str
    price_per_unit: float
    quantity: int
    total_price: float

class CartCalculationRequest(BaseModel):
    items: List[CartItemInput]

class CartCalculationResponse(BaseModel):
    items: List[CartItemOutput]
    total_price: float
    calculated_at: datetime

# Модель для ответа от микросервиса "Каталог"
class AudiobookInfo(BaseModel):
    id: int
    title: str
    price: float
    description: Optional[str] = None
    cover_image_url: Optional[str] = None
    author: Optional[dict] = None
    categories: Optional[List[dict]] = None

async def get_audiobook_info(audiobook_id: int, client: httpx.AsyncClient) -> Optional[AudiobookInfo]:
    """
    Асинхронно получает информацию об аудиокниге из микросервиса "Каталог"
    """
    try:
        response = await client.get(f"http://localhost:8001/api/v1/audiobooks/{audiobook_id}")
        
        if response.status_code == 404:
            # Товар не найден - игнорируем
            return None
        elif response.status_code == 200:
            data = response.json()
            return AudiobookInfo(**data)
        else:
            # Другие ошибки - логируем, но не прерываем процесс
            print(f"Ошибка при получении информации об аудиокниге {audiobook_id}: {response.status_code}")
            return None
            
    except httpx.RequestError as e:
        print(f"Ошибка сети при получении информации об аудиокниге {audiobook_id}: {e}")
        return None
    except Exception as e:
        print(f"Неожиданная ошибка при получении информации об аудиокниге {audiobook_id}: {e}")
        return None

@app.post("/api/v1/cart/calculate", response_model=CartCalculationResponse)
async def calculate_cart(request: CartCalculationRequest):
    """
    Рассчитывает стоимость корзины на основе списка товаров
    
    - Получает информацию о каждой аудиокниге из микросервиса "Каталог"
    - Игнорирует товары, которые не найдены в каталоге
    - Рассчитывает общую стоимость корзины
    """
    
    if not request.items:
        return CartCalculationResponse(
            items=[],
            total_price=0.0,
            calculated_at=datetime.now()
        )
    
    # Создаем HTTP клиент для асинхронных запросов
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Получаем информацию о всех аудиокнигах параллельно
        tasks = [
            get_audiobook_info(item.audiobook_id, client) 
            for item in request.items
        ]
        
        audiobook_infos = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Обрабатываем результаты и формируем выходные данные
    cart_items = []
    total_price = 0.0
    
    for item, audiobook_info in zip(request.items, audiobook_infos):
        # Пропускаем товары, которые не найдены или вызвали ошибку
        if audiobook_info is None or isinstance(audiobook_info, Exception):
            continue
            
        item_total = audiobook_info.price * item.quantity
        
        cart_item = CartItemOutput(
            audiobook_id=item.audiobook_id,
            title=audiobook_info.title,
            price_per_unit=audiobook_info.price,
            quantity=item.quantity,
            total_price=item_total
        )
        
        cart_items.append(cart_item)
        total_price += item_total
    
    return CartCalculationResponse(
        items=cart_items,
        total_price=total_price,
        calculated_at=datetime.now()
    )

@app.get("/health")
async def health_check():
    """
    Эндпоинт для проверки состояния сервиса
    """
    return {"status": "healthy", "service": "cart"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
