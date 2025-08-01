#!/usr/bin/env python3
"""
Тесты для микросервиса 'Заказы'
"""

import pytest
import httpx
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

# Добавляем корневую директорию проекта в путь
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from main import app
from schemas import OrderCreateRequest, CartItemInput


class TestOrdersService:
    """Тесты для микросервиса заказов"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.client = TestClient(app)
    
    def test_root_endpoint(self):
        """Тест корневого эндпоинта"""
        response = self.client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Микросервис 'Заказы' работает"
        assert "create_order" in data["endpoints"]
    
    def test_health_check(self):
        """Тест health check эндпоинта"""
        response = self.client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "orders"
    
    @patch('services.OrderService.validate_cart_with_cart_service')
    @patch('services.OrderService.create_order_transaction')
    def test_create_order_success(self, mock_create_order, mock_validate_cart):
        """Тест успешного создания заказа"""
        # Мокаем ответ от сервиса корзины
        mock_validate_cart.return_value = type('obj', (object,), {
            'items': [
                {
                    'audiobook_id': 1,
                    'title': 'Тестовая книга',
                    'price_per_unit': 100.0,
                    'quantity': 2
                }
            ],
            'total_price': 200.0,
            'calculated_at': '2024-01-01T00:00:00Z'
        })()
        
        # Мокаем создание заказа
        mock_order = type('obj', (object,), {
            'id': 1,
            'order_number': 'ORD-20240101000000-12345678',
            'total_amount': 200.0,
            'status': 'pending',
            'created_at': '2024-01-01T00:00:00Z',
            'updated_at': None,
            'items': [
                type('obj', (object,), {
                    'id': 1,
                    'audiobook_id': 1,
                    'title': 'Тестовая книга',
                    'price_per_unit': 100.0,
                    'quantity': 2,
                    'total_price': 200.0,
                    'created_at': '2024-01-01T00:00:00Z'
                })()
            ]
        })()
        mock_create_order.return_value = mock_order
        
        # Тестовые данные
        request_data = {
            "items": [
                {"audiobook_id": 1, "quantity": 2}
            ]
        }
        
        response = self.client.post("/api/v1/orders", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["order_number"] == "ORD-20240101000000-12345678"
        assert data["total_amount"] == 200.0
        assert data["status"] == "pending"
        assert len(data["items"]) == 1
    
    @patch('services.OrderService.validate_cart_with_cart_service')
    def test_create_order_empty_cart(self, mock_validate_cart):
        """Тест создания заказа с пустой корзиной"""
        # Мокаем пустой ответ от сервиса корзины
        mock_validate_cart.return_value = type('obj', (object,), {
            'items': [],
            'total_price': 0.0,
            'calculated_at': '2024-01-01T00:00:00Z'
        })()
        
        request_data = {
            "items": [
                {"audiobook_id": 999, "quantity": 1}
            ]
        }
        
        response = self.client.post("/api/v1/orders", json=request_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "Корзина пуста" in data["detail"]
    
    @patch('services.OrderService.validate_cart_with_cart_service')
    def test_create_order_cart_service_unavailable(self, mock_validate_cart):
        """Тест создания заказа при недоступности сервиса корзины"""
        # Мокаем ошибку сервиса корзины
        mock_validate_cart.side_effect = Exception("Сервис недоступен")
        
        request_data = {
            "items": [
                {"audiobook_id": 1, "quantity": 1}
            ]
        }
        
        response = self.client.post("/api/v1/orders", json=request_data)
        
        assert response.status_code == 503
        data = response.json()
        assert "Сервис корзины недоступен" in data["detail"]


class TestOrderSchemas:
    """Тесты для схем данных"""
    
    def test_cart_item_input_validation(self):
        """Тест валидации CartItemInput"""
        # Валидные данные
        valid_item = CartItemInput(audiobook_id=1, quantity=2)
        assert valid_item.audiobook_id == 1
        assert valid_item.quantity == 2
        
        # Невалидные данные (количество <= 0)
        with pytest.raises(ValueError):
            CartItemInput(audiobook_id=1, quantity=0)
        
        with pytest.raises(ValueError):
            CartItemInput(audiobook_id=1, quantity=-1)
    
    def test_order_create_request_validation(self):
        """Тест валидации OrderCreateRequest"""
        # Валидные данные
        valid_request = OrderCreateRequest(
            items=[
                CartItemInput(audiobook_id=1, quantity=2),
                CartItemInput(audiobook_id=2, quantity=1)
            ]
        )
        assert len(valid_request.items) == 2
        
        # Пустой список товаров
        empty_request = OrderCreateRequest(items=[])
        assert len(empty_request.items) == 0


if __name__ == "__main__":
    print("🧪 Запуск тестов микросервиса 'Заказы'...")
    pytest.main([__file__, "-v"]) 