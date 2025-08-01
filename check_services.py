#!/usr/bin/env python3
"""
Проверка состояния микросервисов
"""

import socket
import requests
import json

def check_port(host, port):
    """Проверяет, открыт ли порт"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def test_catalog():
    """Тестирует микросервис 'Каталог'"""
    print("🔍 Проверка микросервиса 'Каталог' (порт 8001)...")
    
    if not check_port('localhost', 8001):
        print("❌ Порт 8001 не открыт")
        return False
    
    try:
        response = requests.get("http://localhost:8001/health", timeout=3)
        if response.status_code == 200:
            print("✅ Микросервис 'Каталог' работает")
            return True
        else:
            print(f"❌ Ошибка HTTP: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False

def test_cart():
    """Тестирует микросервис 'Корзина'"""
    print("🔍 Проверка микросервиса 'Корзина' (порт 8002)...")
    
    if not check_port('localhost', 8002):
        print("❌ Порт 8002 не открыт")
        return False
    
    try:
        response = requests.get("http://localhost:8002/health", timeout=3)
        if response.status_code == 200:
            print("✅ Микросервис 'Корзина' работает")
            return True
        else:
            print(f"❌ Ошибка HTTP: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False

def main():
    print("🚀 Проверка состояния микросервисов")
    print("=" * 40)
    
    catalog_ok = test_catalog()
    cart_ok = test_cart()
    
    print("\n📊 Результаты:")
    print(f"   Каталог: {'✅' if catalog_ok else '❌'}")
    print(f"   Корзина: {'✅' if cart_ok else '❌'}")
    
    if catalog_ok and cart_ok:
        print("\n🎉 Все сервисы работают!")
        
        # Тестируем расчет корзины
        print("\n🧪 Тестирование расчета корзины...")
        try:
            cart_data = {
                "items": [
                    {"audiobook_id": 1, "quantity": 2},
                    {"audiobook_id": 2, "quantity": 1}
                ]
            }
            
            response = requests.post(
                "http://localhost:8002/api/v1/cart/calculate",
                json=cart_data,
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Расчет корзины успешен!")
                print(f"   Общая стоимость: {result['total_price']}")
                print(f"   Товаров в корзине: {len(result['items'])}")
            else:
                print(f"❌ Ошибка расчета: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Ошибка тестирования: {e}")
    else:
        print("\n⚠️  Некоторые сервисы не работают")
        print("   Запустите:")
        print("   - Микросервис 'Каталог': cd services/catalog && python main.py")
        print("   - Микросервис 'Корзина': cd services/cart && python run_app.py")

if __name__ == "__main__":
    main() 