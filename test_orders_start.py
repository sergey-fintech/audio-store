#!/usr/bin/env python3
"""
Тестовый скрипт для проверки запуска микросервиса 'Заказы'
"""

import subprocess
import time
import requests
import sys
import os

def test_orders_startup():
    """Тестирует запуск микросервиса заказов"""
    print("🧪 Тестирование запуска микросервиса 'Заказы'")
    print("=" * 50)
    
    try:
        # Запускаем микросервис
        print("🚀 Запуск микросервиса 'Заказы'...")
        process = subprocess.Popen(
            [sys.executable, "-m", "services.orders.run_app"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        print(f"✅ Процесс запущен (PID: {process.pid})")
        
        # Ждем запуска
        print("⏳ Ожидание запуска сервиса...")
        for i in range(30):
            try:
                response = requests.get("http://localhost:8003/health", timeout=2)
                if response.status_code == 200:
                    print("✅ Микросервис 'Заказы' готов к работе!")
                    print(f"   Ответ: {response.json()}")
                    break
            except:
                pass
            
            time.sleep(1)
            if (i + 1) % 5 == 0:
                print(f"   ... еще {30 - i - 1} секунд")
        else:
            print("❌ Микросервис не запустился за 30 секунд")
            
            # Проверяем вывод процесса
            try:
                stdout, stderr = process.communicate(timeout=1)
                if stdout:
                    print("📋 STDOUT:")
                    print(stdout.decode('utf-8', errors='ignore'))
                if stderr:
                    print("❌ STDERR:")
                    print(stderr.decode('utf-8', errors='ignore'))
            except:
                pass
            
            process.terminate()
            return False
        
        # Тестируем основные эндпоинты
        print("\n🧪 Тестирование эндпоинтов...")
        
        # Корневой эндпоинт
        try:
            response = requests.get("http://localhost:8003/")
            if response.status_code == 200:
                print("✅ Корневой эндпоинт работает")
            else:
                print(f"❌ Корневой эндпоинт: {response.status_code}")
        except Exception as e:
            print(f"❌ Ошибка корневого эндпоинта: {e}")
        
        # Список заказов
        try:
            response = requests.get("http://localhost:8003/api/v1/orders")
            if response.status_code == 200:
                print("✅ Эндпоинт списка заказов работает")
            else:
                print(f"❌ Список заказов: {response.status_code}")
        except Exception as e:
            print(f"❌ Ошибка списка заказов: {e}")
        
        print("\n🛑 Остановка сервиса...")
        process.terminate()
        process.wait(timeout=5)
        print("✅ Сервис остановлен")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    success = test_orders_startup()
    if success:
        print("\n🎉 Тест прошел успешно!")
    else:
        print("\n💥 Тест провален!")
    
    print("\n📋 Заключение:")
    print("   - Микросервис 'Заказы' можно запустить командой:")
    print("   python -m services.orders.run_app")
    print("   - После запуска он доступен по адресу: http://localhost:8003")
    print("   - API документация: http://localhost:8003/docs") 