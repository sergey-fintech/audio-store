#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы микросервиса "Корзина"
"""

import httpx
import asyncio
import json

async def test_cart_calculation():
    """
    Тестирует эндпоинт расчета корзины
    """
    
    # Тестовые данные
    test_data = {
        "items": [
            {
                "audiobook_id": 1,
                "quantity": 2
            },
            {
                "audiobook_id": 2,
                "quantity": 1
            },
            {
                "audiobook_id": 999,  # Несуществующий товар
                "quantity": 3
            }
        ]
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8001/api/v1/cart/calculate",
                json=test_data,
                timeout=30.0
            )
            
            print(f"Статус ответа: {response.status_code}")
            print(f"Заголовки: {response.headers}")
            
            if response.status_code == 200:
                result = response.json()
                print("Результат расчета корзины:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                print(f"Ошибка: {response.text}")
                
        except httpx.RequestError as e:
            print(f"Ошибка сети: {e}")
        except Exception as e:
            print(f"Неожиданная ошибка: {e}")

async def test_health_check():
    """
    Тестирует эндпоинт проверки состояния
    """
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://localhost:8001/health")
            print(f"Health check статус: {response.status_code}")
            print(f"Health check ответ: {response.json()}")
            
        except httpx.RequestError as e:
            print(f"Ошибка сети при health check: {e}")

async def main():
    """
    Основная функция для запуска тестов
    """
    print("Тестирование микросервиса 'Корзина'")
    print("=" * 50)
    
    # Проверяем состояние сервиса
    print("\n1. Проверка состояния сервиса:")
    await test_health_check()
    
    # Тестируем расчет корзины
    print("\n2. Тестирование расчета корзины:")
    await test_cart_calculation()

if __name__ == "__main__":
    asyncio.run(main()) 