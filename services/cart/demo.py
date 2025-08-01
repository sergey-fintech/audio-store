#!/usr/bin/env python3
"""
Демонстрационный скрипт для микросервиса "Корзина"
Показывает примеры использования API
"""

import httpx
import asyncio
import json
from datetime import datetime

async def demo_cart_calculation():
    """
    Демонстрирует работу расчета корзины
    """
    print("🚀 Демонстрация микросервиса 'Корзина'")
    print("=" * 60)
    
    # Пример 1: Корзина с существующими товарами
    print("\n📋 Пример 1: Расчет корзины с существующими товарами")
    cart_data_1 = {
        "items": [
            {"audiobook_id": 1, "quantity": 2},
            {"audiobook_id": 2, "quantity": 1},
            {"audiobook_id": 3, "quantity": 3}
        ]
    }
    
    await test_cart_request(cart_data_1, "Корзина с существующими товарами")
    
    # Пример 2: Корзина с несуществующими товарами
    print("\n📋 Пример 2: Расчет корзины с несуществующими товарами")
    cart_data_2 = {
        "items": [
            {"audiobook_id": 1, "quantity": 1},
            {"audiobook_id": 999, "quantity": 2},  # Несуществующий товар
            {"audiobook_id": 888, "quantity": 1}   # Несуществующий товар
        ]
    }
    
    await test_cart_request(cart_data_2, "Корзина с несуществующими товарами")
    
    # Пример 3: Пустая корзина
    print("\n📋 Пример 3: Пустая корзина")
    cart_data_3 = {
        "items": []
    }
    
    await test_cart_request(cart_data_3, "Пустая корзина")
    
    # Пример 4: Корзина только с несуществующими товарами
    print("\n📋 Пример 4: Корзина только с несуществующими товарами")
    cart_data_4 = {
        "items": [
            {"audiobook_id": 999, "quantity": 1},
            {"audiobook_id": 888, "quantity": 2}
        ]
    }
    
    await test_cart_request(cart_data_4, "Корзина только с несуществующими товарами")

async def test_cart_request(cart_data, description):
    """
    Тестирует запрос к API корзины
    """
    print(f"\n🔍 Тестирование: {description}")
    print(f"📤 Отправляем данные: {json.dumps(cart_data, indent=2, ensure_ascii=False)}")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                "http://localhost:8001/api/v1/cart/calculate",
                json=cart_data
            )
            
            print(f"📥 Статус ответа: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Результат расчета:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
                
                # Анализ результатов
                total_items = len(result["items"])
                total_price = result["total_price"]
                print(f"📊 Анализ: {total_items} товаров, общая стоимость: {total_price}")
                
            else:
                print(f"❌ Ошибка: {response.text}")
                
        except httpx.RequestError as e:
            print(f"❌ Ошибка сети: {e}")
        except Exception as e:
            print(f"❌ Неожиданная ошибка: {e}")

async def check_service_health():
    """
    Проверяет состояние сервиса
    """
    print("\n🏥 Проверка состояния сервиса...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://localhost:8001/health")
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ Сервис работает: {health_data}")
                return True
            else:
                print(f"❌ Сервис недоступен: {response.status_code}")
                return False
        except httpx.RequestError:
            print("❌ Сервис недоступен (ошибка сети)")
            return False

async def main():
    """
    Основная функция демонстрации
    """
    print("🎯 Демонстрация микросервиса 'Корзина'")
    print("=" * 60)
    
    # Проверяем доступность сервиса
    if not await check_service_health():
        print("\n⚠️  Убедитесь, что микросервис 'Корзина' запущен на порту 8001")
        print("   Запустите: python run_app.py")
        return
    
    # Запускаем демонстрацию
    await demo_cart_calculation()
    
    print("\n" + "=" * 60)
    print("🎉 Демонстрация завершена!")
    print("\n💡 Примечания:")
    print("   - Товары с ID 999, 888 и другие несуществующие ID игнорируются")
    print("   - Сервис работает асинхронно и параллельно запрашивает информацию")
    print("   - Время расчета указано в поле 'calculated_at'")

if __name__ == "__main__":
    asyncio.run(main()) 