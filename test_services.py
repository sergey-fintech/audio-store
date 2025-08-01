#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы микросервисов
"""

import requests
import json
import time

def test_catalog_service():
    """Тестирует микросервис 'Каталог'"""
    print("🔍 Тестирование микросервиса 'Каталог'...")
    
    try:
        # Проверка состояния сервиса
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code == 200:
            print("✅ Микросервис 'Каталог' работает")
            print(f"   Ответ: {response.json()}")
        else:
            print(f"❌ Ошибка: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Не удалось подключиться к микросервису 'Каталог': {e}")
        return False
    
    try:
        # Проверка получения аудиокниги
        response = requests.get("http://localhost:8001/audiobooks/1", timeout=5)
        if response.status_code == 200:
            audiobook = response.json()
            print(f"✅ Получена аудиокнига: {audiobook['title']}")
            print(f"   Цена: {audiobook['price']}")
        else:
            print(f"❌ Ошибка при получении аудиокниги: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка при получении аудиокниги: {e}")
        return False
    
    return True

def test_cart_service():
    """Тестирует микросервис 'Корзина'"""
    print("\n🔍 Тестирование микросервиса 'Корзина'...")
    
    try:
        # Проверка состояния сервиса
        response = requests.get("http://localhost:8002/health", timeout=5)
        if response.status_code == 200:
            print("✅ Микросервис 'Корзина' работает")
            print(f"   Ответ: {response.json()}")
        else:
            print(f"❌ Ошибка: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Не удалось подключиться к микросервису 'Корзина': {e}")
        return False
    
    try:
        # Тестирование расчета корзины
        cart_data = {
            "items": [
                {"audiobook_id": 1, "quantity": 2},
                {"audiobook_id": 2, "quantity": 1}
            ]
        }
        
        response = requests.post(
            "http://localhost:8002/api/v1/cart/calculate",
            json=cart_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Расчет корзины выполнен успешно")
            print(f"   Общая стоимость: {result['total_price']}")
            print(f"   Количество товаров: {len(result['items'])}")
            
            for item in result['items']:
                print(f"   - {item['title']}: {item['quantity']} x {item['price_per_unit']} = {item['total_price']}")
        else:
            print(f"❌ Ошибка при расчете корзины: {response.status_code}")
            print(f"   Ответ: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Ошибка при расчете корзины: {e}")
        return False
    
    return True

def main():
    """Основная функция тестирования"""
    print("🚀 Тестирование микросервисов Audio Store")
    print("=" * 50)
    
    # Тестируем микросервис "Каталог"
    catalog_ok = test_catalog_service()
    
    # Тестируем микросервис "Корзина"
    cart_ok = test_cart_service()
    
    print("\n" + "=" * 50)
    print("📊 Результаты тестирования:")
    print(f"   Микросервис 'Каталог': {'✅ Работает' if catalog_ok else '❌ Не работает'}")
    print(f"   Микросервис 'Корзина': {'✅ Работает' if cart_ok else '❌ Не работает'}")
    
    if catalog_ok and cart_ok:
        print("\n🎉 Все сервисы работают корректно!")
    else:
        print("\n⚠️  Некоторые сервисы не работают. Проверьте их запуск.")

if __name__ == "__main__":
    main() 