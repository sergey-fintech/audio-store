#!/usr/bin/env python3
"""
Скрипт для запуска микросервисов
"""

import subprocess
import time
import requests
import sys
import os
import signal
import atexit

# Глобальные переменные для хранения процессов
processes = []

def cleanup_processes():
    """Очищает все запущенные процессы при выходе"""
    for process in processes:
        try:
            if process.poll() is None:  # Процесс еще работает
                process.terminate()
                process.wait(timeout=5)
        except:
            pass

# Регистрируем функцию очистки
atexit.register(cleanup_processes)

def start_catalog_service():
    """Запускает микросервис 'Каталог'"""
    print("🚀 Запуск микросервиса 'Каталог'...")
    
    try:
        # Запускаем сервис из корневой директории
        process = subprocess.Popen(
            [sys.executable, "services/catalog/main.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        print(f"✅ Микросервис 'Каталог' запущен (PID: {process.pid})")
        processes.append(process)
        return process
    except Exception as e:
        print(f"❌ Ошибка запуска микросервиса 'Каталог': {e}")
        return None

def start_cart_service():
    """Запускает микросервис 'Корзина'"""
    print("🚀 Запуск микросервиса 'Корзина'...")
    
    try:
        # Запускаем сервис из корневой директории
        process = subprocess.Popen(
            [sys.executable, "services/cart/run_app.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        print(f"✅ Микросервис 'Корзина' запущен (PID: {process.pid})")
        processes.append(process)
        return process
    except Exception as e:
        print(f"❌ Ошибка запуска микросервиса 'Корзина': {e}")
        return None

def start_orders_service():
    """Запускает микросервис 'Заказы'"""
    print("🚀 Запуск микросервиса 'Заказы'...")
    
    try:
        # Запускаем сервис из корневой директории
        process = subprocess.Popen(
            [sys.executable, "services/orders/run_app.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        print(f"✅ Микросервис 'Заказы' запущен (PID: {process.pid})")
        processes.append(process)
        return process
    except Exception as e:
        print(f"❌ Ошибка запуска микросервиса 'Заказы': {e}")
        return None

def wait_for_service(url, service_name, timeout=30):
    """Ожидает запуска сервиса"""
    print(f"⏳ Ожидание запуска {service_name}...")
    
    for i in range(timeout):
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                print(f"✅ {service_name} готов к работе")
                return True
        except:
            pass
        
        time.sleep(1)
        if (i + 1) % 5 == 0:
            print(f"   ... еще {timeout - i - 1} секунд")
    
    print(f"❌ {service_name} не запустился за {timeout} секунд")
    return False

def test_cart_calculation():
    """Тестирует расчет корзины"""
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
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Расчет корзины успешен!")
            print(f"   Общая стоимость: {result['total_price']}")
            print(f"   Товаров в корзине: {len(result['items'])}")
            
            for item in result['items']:
                print(f"   - {item['title']}: {item['quantity']} x {item['price_per_unit']} = {item['total_price']}")
            
            return True
        else:
            print(f"❌ Ошибка расчета: {response.status_code}")
            print(f"   Ответ: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        return False

def signal_handler(signum, frame):
    """Обработчик сигнала для корректного завершения"""
    print("\n🛑 Получен сигнал остановки. Завершаем работу...")
    cleanup_processes()
    sys.exit(0)

def main():
    """Основная функция"""
    print("🎯 Запуск микросервисов Audio Store")
    print("=" * 50)
    
    # Устанавливаем обработчик сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Убеждаемся, что мы в корневой директории
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Запускаем микросервис "Каталог"
    catalog_process = start_catalog_service()
    if not catalog_process:
        print("❌ Не удалось запустить микросервис 'Каталог'")
        return
    
    # Ждем запуска микросервиса "Каталог"
    if not wait_for_service("http://localhost:8001/health", "Микросервис 'Каталог'"):
        print("❌ Микросервис 'Каталог' не запустился")
        return
    
    # Запускаем микросервис "Корзина"
    cart_process = start_cart_service()
    if not cart_process:
        print("❌ Не удалось запустить микросервис 'Корзина'")
        return
    
    # Ждем запуска микросервиса "Корзина"
    if not wait_for_service("http://localhost:8002/health", "Микросервис 'Корзина'"):
        print("❌ Микросервис 'Корзина' не запустился")
        return
    
    # Запускаем микросервис "Заказы"
    orders_process = start_orders_service()
    if not orders_process:
        print("❌ Не удалось запустить микросервис 'Заказы'")
        return
    
    # Ждем запуска микросервиса "Заказы"
    if not wait_for_service("http://localhost:8003/health", "Микросервис 'Заказы'"):
        print("❌ Микросервис 'Заказы' не запустился")
        return
    
    print("\n🎉 Все сервисы запущены!")
    print("   - Каталог: http://localhost:8001")
    print("   - Корзина: http://localhost:8002")
    print("   - Заказы: http://localhost:8003")
    
    # Тестируем расчет корзины
    test_cart_calculation()
    
    print("\n📋 Для остановки сервисов нажмите Ctrl+C")
    
    try:
        # Ждем завершения процессов
        while True:
            time.sleep(1)
            # Проверяем, что все процессы еще работают
            for process in processes:
                if process.poll() is not None:
                    print(f"⚠️  Процесс {process.pid} завершился")
    except KeyboardInterrupt:
        print("\n🛑 Остановка сервисов...")
        cleanup_processes()
        print("✅ Сервисы остановлены")

if __name__ == "__main__":
    main() 