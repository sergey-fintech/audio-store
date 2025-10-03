from typing import List, Dict
from datetime import datetime

import sys
import os

# Добавляем путь к корневой директории проекта
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from services.shared_services.catalog import CatalogService, get_catalog_service
from pydantic import BaseModel

class CartItemInput(BaseModel):
    audiobook_id: int
    quantity: int

class CartItemOutput(BaseModel):
    audiobook_id: int
    title: str
    price_per_unit: float
    quantity: int
    total_price: float

class CartCalculationResult(BaseModel):
    items: List[CartItemOutput]
    total_price: float
    calculated_at: datetime

class CartService:
    def __init__(self, catalog_service: CatalogService):
        self.catalog_service = catalog_service

    def calculate_cart(self, items: List[CartItemInput]) -> CartCalculationResult:
        """
        Рассчитывает стоимость корзины.
        """
        if not items:
            return CartCalculationResult(
                items=[],
                total_price=0.0,
                calculated_at=datetime.now()
            )

        audiobook_ids = [item.audiobook_id for item in items]
        audiobooks = self.catalog_service.get_audiobooks_by_ids(audiobook_ids)
        audiobooks_map = {ab.id: ab for ab in audiobooks}

        cart_items_output = []
        total_price = 0.0

        for item in items:
            audiobook = audiobooks_map.get(item.audiobook_id)
            if audiobook:
                item_total = float(audiobook.price) * item.quantity
                cart_items_output.append(
                    CartItemOutput(
                        audiobook_id=item.audiobook_id,
                        title=audiobook.title,
                        price_per_unit=float(audiobook.price),
                        quantity=item.quantity,
                        total_price=round(item_total, 2),
                    )
                )
                total_price += item_total
        
        return CartCalculationResult(
            items=cart_items_output,
            total_price=round(total_price, 2),
            calculated_at=datetime.now()
        )

def get_cart_service() -> CartService:
    """Фабрика для получения экземпляра CartService."""
    catalog_service = get_catalog_service()
    return CartService(catalog_service)
