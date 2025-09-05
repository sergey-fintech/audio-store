#!/usr/bin/env python3
"""
Скрипт для тестирования доступности микросервисов
"""

import requests
import json
import time

def test_service(url, name):
    """Тестирует доступность сервиса"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✅ {name} доступен: {url}")
            return True
        else:
            print(f"❌ {name} недоступен (статус {response.status_code}): {url}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ {name} недоступен: {url} - {e}")
        return False

def test_cart_api():
    """Тестирует API корзины"""
    url = "http://localhost:8004/api/v1/cart/calculate"
    test_data = {
        "items": [
            {"audiobook_id": 1, "quantity": 2},
            {"audiobook_id": 2, "quantity": 1}
        ]
    }
    
    try:
        response = requests.post(url, json=test_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Cart API работает: получено {len(data.get('items', []))} товаров")
            return True
        else:
            print(f"❌ Cart API ошибка (статус {response.status_code}): {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cart API недоступен: {e}")
        return False

def test_orders_api():
    """Тестирует API заказов"""
    url = "http://localhost:8003/health"
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✅ Orders API доступен: {url}")
            return True
        else:
            print(f"❌ Orders API ошибка (статус {response.status_code})")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Orders API недоступен: {e}")
        return False

def main():
    print("🔍 Тестирование микросервисов...")
    print("=" * 50)
    
    # Тестируем доступность сервисов
    services = [
        ("http://localhost:8000", "Веб-сервер"),
        ("http://localhost:8001/health", "Auth Service"),
        ("http://localhost:8002/health", "Catalog Service"),
        ("http://localhost:8004/health", "Cart Service"),
        ("http://localhost:8003/health", "Orders Service"),
    ]
    
    available_services = 0
    for url, name in services:
        if test_service(url, name):
            available_services += 1
        time.sleep(1)
    
    print("\n" + "=" * 50)
    print(f"📊 Доступно сервисов: {available_services}/{len(services)}")
    
    # Тестируем API корзины
    print("\n🧪 Тестирование API корзины...")
    test_cart_api()
    
    # Тестируем API заказов
    print("\n🧪 Тестирование API заказов...")
    test_orders_api()
    
    print("\n" + "=" * 50)
    print("🎯 Тестирование завершено!")

if __name__ == "__main__":
    main() 