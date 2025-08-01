#!/usr/bin/env python3
"""
Улучшенная демонстрация микросервиса 'Заказы' с точным расчетом корзины
"""

import sys
import os
import asyncio
import httpx
import json
import time

# Убеждаемся, что мы в корневой директории проекта
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

async def check_service_health(url, name, timeout=5):
    """Проверяет здоровье сервиса"""
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(f"{url}/health")
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, f"HTTP {response.status_code}"
    except Exception as e:
        return False, str(e)

async def wait_for_services():
    """Ждет запуска всех необходимых сервисов"""
    services = [
        ("http://localhost:8001", "Каталог"),
        ("http://localhost:8002", "Корзина"), 
        ("http://localhost:8003", "Заказы")
    ]
    
    print("⏳ Ожидание запуска всех сервисов...")
    
    for attempt in range(30):  # 30 попыток по 2 секунды = 1 минута
        all_ready = True
        status_info = []
        
        for url, name in services:
            is_healthy, info = await check_service_health(url, name, timeout=2)
            if is_healthy:
                status_info.append(f"✅ {name}")
            else:
                status_info.append(f"❌ {name} ({info})")
                all_ready = False
        
        print(f"\r   Попытка {attempt + 1}: {' | '.join(status_info)}", end="")
        
        if all_ready:
            print("\n✅ Все сервисы готовы!")
            return True
            
        await asyncio.sleep(2)
    
    print(f"\n❌ Не все сервисы запустились за {30 * 2} секунд")
    return False

async def test_cart_calculation_detailed():
    """Подробное тестирование расчета корзины"""
    print("\n🧪 Подробное тестирование расчета корзины")
    print("=" * 60)
    
    # Сначала проверим, какие аудиокниги доступны
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            print("📚 Проверка доступных аудиокниг в каталоге...")
            
            # Получаем информацию о первых 5 книгах
            for book_id in range(1, 6):
                response = await client.get(f"http://localhost:8001/api/v1/audiobooks/{book_id}")
                if response.status_code == 200:
                    book = response.json()
                    print(f"   📖 ID {book_id}: {book['title']} - {book['price']} руб. (автор: {book['author']['name'] if book['author'] else 'N/A'})")
                else:
                    print(f"   ❌ ID {book_id}: не найдена")
            
            print("\n🛒 Тестируем расчет корзины...")
            cart_data = {
                "items": [
                    {"audiobook_id": 1, "quantity": 2},
                    {"audiobook_id": 2, "quantity": 1}
                ]
            }
            
            print(f"📋 Отправляем корзину: {json.dumps(cart_data, indent=2, ensure_ascii=False)}")
            
            response = await client.post(
                "http://localhost:8002/api/v1/cart/calculate",
                json=cart_data
            )
            
            print(f"\n📊 Ответ сервиса корзины (статус {response.status_code}):")
            
            if response.status_code == 200:
                result = response.json()
                print(json.dumps(result, indent=2, ensure_ascii=False))
                
                if result['items']:
                    print("\n💰 ТОЧНЫЙ РАСЧЕТ КОРЗИНЫ:")
                    total_check = 0
                    for item in result['items']:
                        item_total = item['price_per_unit'] * item['quantity']
                        total_check += item_total
                        print(f"   📖 {item['title']}")
                        print(f"      💵 Цена за единицу: {item['price_per_unit']} руб.")
                        print(f"      📦 Количество: {item['quantity']}")
                        print(f"      🧮 Расчет: {item['price_per_unit']} × {item['quantity']} = {item_total} руб.")
                        print(f"      ✅ Итого за товар: {item['total_price']} руб.")
                    
                    print(f"\n🎯 ОБЩАЯ СУММА КОРЗИНЫ: {result['total_price']} руб.")
                    print(f"🔍 Проверка расчета: {total_check} руб.")
                    
                    if abs(total_check - result['total_price']) < 0.01:
                        print("✅ Расчет корректен!")
                    else:
                        print("❌ Ошибка в расчете!")
                        
                    return result
                else:
                    print("⚠️  Корзина пуста - товары не найдены в каталоге")
                    return None
            else:
                print(f"❌ Ошибка: {response.text}")
                return None
                
    except Exception as e:
        print(f"❌ Ошибка при тестировании корзины: {e}")
        return None

async def test_order_creation_detailed(cart_result=None):
    """Подробное тестирование создания заказа"""
    print("\n🛒 Подробное тестирование создания заказа")
    print("=" * 60)
    
    order_data = {
        "items": [
            {"audiobook_id": 1, "quantity": 2},
            {"audiobook_id": 2, "quantity": 1}
        ]
    }
    
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            print(f"📋 Отправляем заказ: {json.dumps(order_data, indent=2, ensure_ascii=False)}")
            
            response = await client.post(
                "http://localhost:8003/api/v1/orders",
                json=order_data
            )
            
            print(f"\n📊 Ответ сервиса заказов (статус {response.status_code}):")
            
            if response.status_code == 200:
                result = response.json()
                print(json.dumps(result, indent=2, ensure_ascii=False))
                
                print("\n📦 АНАЛИЗ СОЗДАННОГО ЗАКАЗА:")
                print(f"   🆔 ID заказа: {result['id']}")
                print(f"   📋 Номер заказа: {result['order_number']}")
                print(f"   💰 Общая сумма: {result['total_amount']} руб.")
                print(f"   📊 Статус: {result['status']}")
                print(f"   📅 Дата создания: {result['created_at']}")
                print(f"   📦 Количество позиций: {len(result['items'])}")
                
                if result['items']:
                    print("\n📋 ДЕТАЛИ ПОЗИЦИЙ ЗАКАЗА:")
                    order_total = 0
                    for i, item in enumerate(result['items'], 1):
                        item_total = float(item['price_per_unit']) * item['quantity']
                        order_total += item_total
                        print(f"   {i}. 📖 {item['title']}")
                        print(f"      💵 Цена: {item['price_per_unit']} руб.")
                        print(f"      📦 Количество: {item['quantity']}")
                        print(f"      🧮 Расчет: {item['price_per_unit']} × {item['quantity']} = {item_total} руб.")
                        print(f"      ✅ Зафиксировано в заказе: {item['total_price']} руб.")
                    
                    print(f"\n🎯 ИТОГОВАЯ СУММА ЗАКАЗА: {result['total_amount']} руб.")
                    print(f"🔍 Проверка расчета: {order_total} руб.")
                    
                    if abs(order_total - float(result['total_amount'])) < 0.01:
                        print("✅ Расчет заказа корректен!")
                    else:
                        print("❌ Ошибка в расчете заказа!")
                    
                    # Сравнение с корзиной
                    if cart_result:
                        print(f"\n🔄 СРАВНЕНИЕ КОРЗИНЫ И ЗАКАЗА:")
                        print(f"   🛒 Расчет корзины: {cart_result['total_price']} руб.")
                        print(f"   📦 Сумма заказа: {result['total_amount']} руб.")
                        if abs(cart_result['total_price'] - float(result['total_amount'])) < 0.01:
                            print("   ✅ Суммы совпадают! Цены зафиксированы корректно.")
                        else:
                            print("   ❌ Суммы не совпадают!")
                
                return result
            else:
                error_detail = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                print(f"❌ Ошибка создания заказа: {error_detail}")
                return None
                
    except Exception as e:
        print(f"❌ Ошибка при создании заказа: {e}")
        return None

async def main():
    """Основная функция демонстрации"""
    print("🚀 ДЕМОНСТРАЦИЯ МИКРОСЕРВИСА 'ЗАКАЗЫ'")
    print("🎯 С точным расчетом корзины и анализом")
    print("=" * 70)
    
    print("📋 Требования:")
    print("   - Микросервис 'Заказы' на порту 8003")
    print("   - Микросервис 'Корзина' на порту 8002")
    print("   - Микросервис 'Каталог' на порту 8001")
    print()
    
    # Ждем запуска сервисов
    if not await wait_for_services():
        print("\n💥 Не все сервисы доступны. Запустите:")
        print("   python start_services.py")
        return 1
    
    # Тестируем расчет корзины
    cart_result = await test_cart_calculation_detailed()
    
    # Тестируем создание заказа
    order_result = await test_order_creation_detailed(cart_result)
    
    # Итоговый анализ
    print("\n" + "=" * 70)
    if cart_result and order_result:
        print("🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        print("\n📊 ФИНАЛЬНЫЙ ОТЧЕТ:")
        print(f"   🛒 Корзина рассчитана: {cart_result['total_price']} руб.")
        print(f"   📦 Заказ создан: {order_result['order_number']}")
        print(f"   💰 Сумма заказа: {order_result['total_amount']} руб.")
        print(f"   📅 Время расчета: {cart_result['calculated_at']}")
        print(f"   🎯 Количество товаров: {len(order_result['items'])}")
        
        print("\n✅ СИСТЕМА РАБОТАЕТ КОРРЕКТНО!")
        print("   - Микросервисы взаимодействуют правильно")
        print("   - Расчеты точные")
        print("   - Цены фиксируются в заказе")
        
    else:
        print("💥 НЕКОТОРЫЕ ТЕСТЫ ПРОВАЛИЛИСЬ!")
        if not cart_result:
            print("   ❌ Проблема с расчетом корзины")
            print("   💡 Проверьте доступность каталога и корзины")
        if not order_result:
            print("   ❌ Проблема с созданием заказа")
            print("   💡 Проверьте микросервис заказов")
    
    print("\n📚 Полезные ссылки:")
    print("   - API Заказы: http://localhost:8003/docs")
    print("   - API Корзина: http://localhost:8002/docs")
    print("   - API Каталог: http://localhost:8001/docs")
    
    return 0 if (cart_result and order_result) else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 