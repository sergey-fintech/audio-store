#!/usr/bin/env python3
"""
Тестовый скрипт для API с точным расчетом корзины
"""

import requests
import json
import sys
import os

# Добавляем корневую директорию проекта в путь
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_cart_calculation():
    """Тестирует расчет корзины"""
    print("🧪 Тестирование расчета корзины")
    print("=" * 50)
    
    # Создаем тестовые данные для расчета
    cart_data = {
        "items": [
            {"audiobook_id": 1, "quantity": 2},
            {"audiobook_id": 2, "quantity": 1}
        ]
    }
    
    try:
        print(f"📋 Отправляем запрос на расчет корзины:")
        print(json.dumps(cart_data, indent=2, ensure_ascii=False))
        
        # Отправляем запрос на расчет корзины
        response = requests.post(
            "http://localhost:8002/api/v1/cart/calculate",
            json=cart_data,
            timeout=10
        )
        
        print(f"\n📊 Ответ сервиса корзины (статус {response.status_code}):")
        
        if response.status_code == 200:
            result = response.json()
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            # Анализируем результат
            print("\n💰 Анализ расчета:")
            print(f"   Общая стоимость: {result['total_price']} руб.")
            print(f"   Товаров в корзине: {len(result['items'])}")
            print(f"   Время расчета: {result['calculated_at']}")
            
            if result['items']:
                print("\n📚 Детали по товарам:")
                total_check = 0
                for item in result['items']:
                    item_total = item['price_per_unit'] * item['quantity']
                    total_check += item_total
                    print(f"   - {item['title']}")
                    print(f"     Цена за единицу: {item['price_per_unit']} руб.")
                    print(f"     Количество: {item['quantity']}")
                    print(f"     Итого за товар: {item['total_price']} руб.")
                    print(f"     Проверка расчета: {item['price_per_unit']} × {item['quantity']} = {item_total}")
                
                print(f"\n🔍 Проверка общей суммы: {total_check} руб.")
                if abs(total_check - result['total_price']) < 0.01:
                    print("✅ Расчет корректен!")
                else:
                    print("❌ Ошибка в расчете!")
                    
                return result
            else:
                print("⚠️  Корзина пустая - товары не найдены в каталоге")
                return None
        else:
            print(f"❌ Ошибка: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        return None

def test_order_creation(cart_result=None):
    """Тестирует создание заказа"""
    print("\n🛒 Тестирование создания заказа")
    print("=" * 50)
    
    # Данные заказа
    order_data = {
        "items": [
            {"audiobook_id": 1, "quantity": 2},
            {"audiobook_id": 2, "quantity": 1}
        ]
    }
    
    try:
        print(f"📋 Отправляем запрос на создание заказа:")
        print(json.dumps(order_data, indent=2, ensure_ascii=False))
        
        # Отправляем запрос на создание заказа
        response = requests.post(
            "http://localhost:8003/api/v1/orders",
            json=order_data,
            timeout=10
        )
        
        print(f"\n📊 Ответ сервиса заказов (статус {response.status_code}):")
        
        if response.status_code == 200:
            result = response.json()
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            print("\n📦 Анализ созданного заказа:")
            print(f"   ID заказа: {result['id']}")
            print(f"   Номер заказа: {result['order_number']}")
            print(f"   Общая сумма: {result['total_amount']} руб.")
            print(f"   Статус: {result['status']}")
            print(f"   Дата создания: {result['created_at']}")
            print(f"   Количество позиций: {len(result['items'])}")
            
            if result['items']:
                print("\n📋 Позиции заказа:")
                order_total = 0
                for item in result['items']:
                    item_total = float(item['price_per_unit']) * item['quantity']
                    order_total += item_total
                    print(f"   - {item['title']}")
                    print(f"     Цена: {item['price_per_unit']} руб. × {item['quantity']} = {item['total_price']} руб.")
                
                print(f"\n🔍 Проверка общей суммы заказа: {order_total} руб.")
                if abs(order_total - float(result['total_amount'])) < 0.01:
                    print("✅ Расчет заказа корректен!")
                else:
                    print("❌ Ошибка в расчете заказа!")
                    
                # Сравнение с расчетом корзины
                if cart_result:
                    print(f"\n🔄 Сравнение с расчетом корзины:")
                    print(f"   Корзина: {cart_result['total_price']} руб.")
                    print(f"   Заказ: {result['total_amount']} руб.")
                    if abs(cart_result['total_price'] - float(result['total_amount'])) < 0.01:
                        print("✅ Суммы совпадают!")
                    else:
                        print("❌ Суммы не совпадают!")
                
            return result
        else:
            print(f"❌ Ошибка: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка при создании заказа: {e}")
        return None

def main():
    """Основная функция тестирования"""
    print("🚀 Комплексное тестирование API Audio Store")
    print("=" * 60)
    
    # Тестируем расчет корзины
    cart_result = test_cart_calculation()
    
    # Тестируем создание заказа
    order_result = test_order_creation(cart_result)
    
    print("\n" + "=" * 60)
    if cart_result and order_result:
        print("🎉 Все тесты прошли успешно!")
        print("\n📊 Итоговый расчет:")
        print(f"   Корзина: {cart_result['total_price']} руб.")
        print(f"   Заказ: {order_result['total_amount']} руб.")
        print(f"   Номер заказа: {order_result['order_number']}")
    else:
        print("💥 Некоторые тесты провалились!")
        if not cart_result:
            print("   - Проблема с расчетом корзины")
        if not order_result:
            print("   - Проблема с созданием заказа")

if __name__ == "__main__":
    main() 