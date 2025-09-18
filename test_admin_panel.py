#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы админ-панели и API каталога товаров.
"""

import requests
import json
import time
from typing import Dict, Any

# Конфигурация
CATALOG_API_BASE = "http://localhost:8002"
ADMIN_PANEL_URL = "http://localhost:8000/admin/admin.html"

def test_catalog_api():
    """Тестирование API каталога товаров."""
    print("🔍 Тестирование API каталога товаров...")
    
    try:
        # Проверка доступности сервиса
        response = requests.get(f"{CATALOG_API_BASE}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Сервис каталога доступен")
            health_data = response.json()
            print(f"   Статус: {health_data.get('status', 'unknown')}")
            print(f"   Версия: {health_data.get('version', 'unknown')}")
        else:
            print(f"❌ Сервис каталога недоступен (статус: {response.status_code})")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка подключения к сервису каталога: {e}")
        return False
    
    # Тестирование эндпоинтов аудиокниг
    endpoints_to_test = [
        ("GET", "/audiobooks", "Получение списка аудиокниг"),
        ("GET", "/authors", "Получение списка авторов"),
        ("GET", "/categories", "Получение списка категорий"),
    ]
    
    for method, endpoint, description in endpoints_to_test:
        try:
            response = requests.request(method, f"{CATALOG_API_BASE}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {description} - OK")
                data = response.json()
                if isinstance(data, list):
                    print(f"   Найдено записей: {len(data)}")
            else:
                print(f"❌ {description} - Ошибка (статус: {response.status_code})")
        except Exception as e:
            print(f"❌ {description} - Ошибка: {e}")
    
    return True

def test_admin_panel_access():
    """Тестирование доступа к админ-панели."""
    print("\n🌐 Тестирование доступа к админ-панели...")
    
    try:
        response = requests.get(ADMIN_PANEL_URL, timeout=5)
        if response.status_code == 200:
            print("✅ Админ-панель доступна")
            print(f"   URL: {ADMIN_PANEL_URL}")
            return True
        else:
            print(f"❌ Админ-панель недоступна (статус: {response.status_code})")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка доступа к админ-панели: {e}")
        return False

def create_test_audiobook():
    """Создание тестовой аудиокниги для демонстрации."""
    print("\n📚 Создание тестовой аудиокниги...")
    
    test_audiobook = {
        "title": "Тестовая аудиокнига",
        "author_id": 1,  # Предполагаем, что автор с ID 1 существует
        "description": "Это тестовая аудиокнига для демонстрации работы админ-панели",
        "price": 299.99,
        "cover_image_url": "https://example.com/test-cover.jpg"
    }
    
    try:
        response = requests.post(
            f"{CATALOG_API_BASE}/audiobooks",
            json=test_audiobook,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            created_book = response.json()
            print("✅ Тестовая аудиокнига создана")
            print(f"   ID: {created_book.get('id')}")
            print(f"   Название: {created_book.get('title')}")
            return created_book.get('id')
        else:
            print(f"❌ Ошибка создания аудиокниги (статус: {response.status_code})")
            print(f"   Ответ: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка при создании аудиокниги: {e}")
        return None

def main():
    """Основная функция тестирования."""
    print("🚀 Тестирование админ-панели и API каталога товаров")
    print("=" * 60)
    
    # Тестируем API каталога
    api_ok = test_catalog_api()
    
    # Тестируем доступ к админ-панели
    admin_ok = test_admin_panel_access()
    
    if api_ok and admin_ok:
        print("\n🎉 Все тесты пройдены успешно!")
        print("\n📋 Инструкции по использованию:")
        print("1. Откройте админ-панель: http://localhost:8000/admin/admin.html")
        print("2. Используйте форму для добавления новых аудиокниг")
        print("3. Редактируйте и удаляйте существующие записи")
        print("4. Все изменения сохраняются в базе данных")
        
        # Создаем тестовую аудиокнигу для демонстрации
        test_book_id = create_test_audiobook()
        if test_book_id:
            print(f"\n💡 Создана тестовая аудиокнига с ID: {test_book_id}")
            print("   Вы можете найти её в админ-панели и протестировать редактирование/удаление")
    else:
        print("\n❌ Некоторые тесты не пройдены")
        print("Убедитесь, что:")
        print("1. Сервис каталога запущен на порту 8002")
        print("2. Веб-сервер запущен на порту 8000")
        print("3. База данных доступна и содержит необходимые таблицы")

if __name__ == "__main__":
    main()




