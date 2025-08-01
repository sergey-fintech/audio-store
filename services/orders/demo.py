#!/usr/bin/env python3
"""
Демонстрационный скрипт для тестирования микросервиса 'Заказы'
"""

import asyncio
import httpx
import json
import sys
import os

# Добавляем корневую директорию проекта в путь
if __name__ == "__main__":
    # Если запускается как модуль, путь уже настроен
    # Если запускается напрямую, добавляем путь
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

async def test_orders_service():
    """Тестирует микросервис заказов"""
    
    # URL микросервиса заказов
    orders_url = "http://localhost:8003"
    
    print("🧪 Демонстрация микросервиса 'Заказы'")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        # 1. Проверяем health check
        print("1️⃣ Проверка health check...")
        try:
            response = await client.get(f"{orders_url}/health")
            if response.status_code == 200:
                print("✅ Сервис работает")
                print(f"   Статус: {response.json()}")
            else:
                print(f"❌ Сервис недоступен: {response.status_code}")
                return
        except Exception as e:
            print(f"❌ Не удалось подключиться к сервису: {str(e)}")
            return
        
        # 2. Проверяем корневой эндпоинт
        print("\n2️⃣ Проверка корневого эндпоинта...")
        try:
            response = await client.get(f"{orders_url}/")
            if response.status_code == 200:
                data = response.json()
                print("✅ Корневой эндпоинт работает")
                print(f"   Сообщение: {data['message']}")
                print(f"   Доступные эндпоинты: {list(data['endpoints'].keys())}")
            else:
                print(f"❌ Ошибка корневого эндпоинта: {response.status_code}")
        except Exception as e:
            print(f"❌ Ошибка: {str(e)}")
        
        # 3. Тестируем создание заказа
        print("\n3️⃣ Тестирование создания заказа...")
        
        # Тестовые данные для заказа
        order_data = {
            "items": [
                {
                    "audiobook_id": 1,
                    "quantity": 2
                },
                {
                    "audiobook_id": 2,
                    "quantity": 1
                }
            ]
        }
        
        try:
            print(f"   Отправляем запрос: {json.dumps(order_data, indent=2)}")
            response = await client.post(f"{orders_url}/api/v1/orders", json=order_data)
            
            if response.status_code == 200:
                order = response.json()
                print("✅ Заказ успешно создан!")
                print(f"   ID заказа: {order['id']}")
                print(f"   Номер заказа: {order['order_number']}")
                print(f"   Общая сумма: {order['total_amount']}")
                print(f"   Статус: {order['status']}")
                print(f"   Количество позиций: {len(order['items'])}")
                
                # Сохраняем ID заказа для дальнейших тестов
                order_id = order['id']
                
            elif response.status_code == 503:
                print("⚠️  Сервис корзины недоступен")
                print("   Убедитесь, что микросервис 'Корзина' запущен на порту 8002")
                return
                
            elif response.status_code == 400:
                print("⚠️  Ошибка валидации корзины")
                print(f"   Детали: {response.json()}")
                return
                
            else:
                print(f"❌ Ошибка создания заказа: {response.status_code}")
                print(f"   Ответ: {response.text}")
                return
                
        except Exception as e:
            print(f"❌ Ошибка при создании заказа: {str(e)}")
            return
        
        # 4. Получаем созданный заказ
        print(f"\n4️⃣ Получение заказа по ID {order_id}...")
        try:
            response = await client.get(f"{orders_url}/api/v1/orders/{order_id}")
            
            if response.status_code == 200:
                order = response.json()
                print("✅ Заказ успешно получен!")
                print(f"   Номер: {order['order_number']}")
                print(f"   Сумма: {order['total_amount']}")
                print(f"   Статус: {order['status']}")
                
                # Показываем детали позиций
                print("   Позиции заказа:")
                for i, item in enumerate(order['items'], 1):
                    print(f"     {i}. {item['title']} x {item['quantity']} = {item['total_price']}")
                    
            else:
                print(f"❌ Ошибка получения заказа: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Ошибка при получении заказа: {str(e)}")
        
        # 5. Получаем список всех заказов
        print("\n5️⃣ Получение списка всех заказов...")
        try:
            response = await client.get(f"{orders_url}/api/v1/orders?limit=10")
            
            if response.status_code == 200:
                orders = response.json()
                print(f"✅ Получено заказов: {len(orders)}")
                
                if orders:
                    print("   Последние заказы:")
                    for i, order in enumerate(orders[:3], 1):
                        print(f"     {i}. {order['order_number']} - {order['total_amount']} - {order['status']}")
                        
            else:
                print(f"❌ Ошибка получения списка заказов: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Ошибка при получении списка заказов: {str(e)}")
        
        # 6. Обновляем статус заказа
        print(f"\n6️⃣ Обновление статуса заказа {order_id}...")
        try:
            new_status = "confirmed"
            response = await client.put(f"{orders_url}/api/v1/orders/{order_id}/status?status={new_status}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Статус заказа успешно обновлен!")
                print(f"   Новый статус: {result['new_status']}")
                
            else:
                print(f"❌ Ошибка обновления статуса: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Ошибка при обновлении статуса: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🎉 Демонстрация завершена!")
    print("\n📚 Полезные ссылки:")
    print("   - API документация: http://localhost:8003/docs")
    print("   - ReDoc документация: http://localhost:8003/redoc")
    print("   - Health check: http://localhost:8003/health")


async def test_with_mock_cart():
    """Тестирует микросервис с моком корзины (для случая, когда корзина недоступна)"""
    
    print("\n🔄 Тестирование с моком корзины...")
    print("⚠️  Этот тест покажет, как работает сервис при недоступности корзины")
    
    # Здесь можно добавить тест с моком, если нужно
    print("   (Для полного тестирования запустите микросервис 'Корзина' на порту 8002)")


if __name__ == "__main__":
    print("🚀 Демонстрация микросервиса 'Заказы'")
    print("📋 Требования:")
    print("   - Микросервис 'Заказы' должен быть запущен на порту 8003")
    print("   - Микросервис 'Корзина' должен быть запущен на порту 8002")
    print("   - Микросервис 'Каталог' должен быть запущен на порту 8001")
    print()
    
    # Запускаем основной тест
    asyncio.run(test_orders_service())
    
    # Запускаем тест с моком
    asyncio.run(test_with_mock_cart()) 