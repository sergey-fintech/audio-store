"""
Тестовый файл для проверки CRUD операций с аудиокнигами.
"""

import requests
import json
from decimal import Decimal

# Базовый URL сервиса каталога
BASE_URL = "http://localhost:8002"

def test_crud_operations():
    """Тестирует все CRUD операции для аудиокниг."""
    
    print("🧪 Тестирование CRUD операций для аудиокниг")
    print("=" * 50)
    
    # 1. Создание аудиокниги
    print("\n1. Создание новой аудиокниги...")
    create_data = {
        "title": "Тестовая аудиокнига",
        "author_id": 1,  # Предполагаем, что автор с ID=1 существует
        "price": "29.99",
        "description": "Описание тестовой аудиокниги",
        "cover_image_url": "https://example.com/cover.jpg",
        "category_ids": [1]  # Предполагаем, что категория с ID=1 существует
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/audiobooks", json=create_data)
    print(f"Статус: {response.status_code}")
    
    if response.status_code == 201 or response.status_code == 200:
        created_book = response.json()
        book_id = created_book["id"]
        print(f"✅ Аудиокнига создана с ID: {book_id}")
        print(f"   Название: {created_book['title']}")
        print(f"   Цена: {created_book['price']}")
    else:
        print(f"❌ Ошибка создания: {response.text}")
        return
    
    # 2. Получение аудиокниги по ID
    print(f"\n2. Получение аудиокниги с ID {book_id}...")
    response = requests.get(f"{BASE_URL}/api/v1/audiobooks/{book_id}")
    print(f"Статус: {response.status_code}")
    
    if response.status_code == 200:
        book = response.json()
        print(f"✅ Аудиокнига получена:")
        print(f"   Название: {book['title']}")
        print(f"   Автор: {book['author']['name'] if book['author'] else 'Не указан'}")
    else:
        print(f"❌ Ошибка получения: {response.text}")
    
    # 3. Обновление аудиокниги
    print(f"\n3. Обновление аудиокниги с ID {book_id}...")
    update_data = {
        "title": "Обновленная тестовая аудиокнига",
        "price": "39.99",
        "description": "Обновленное описание"
    }
    
    response = requests.put(f"{BASE_URL}/api/v1/audiobooks/{book_id}", json=update_data)
    print(f"Статус: {response.status_code}")
    
    if response.status_code == 200:
        updated_book = response.json()
        print(f"✅ Аудиокнига обновлена:")
        print(f"   Новое название: {updated_book['title']}")
        print(f"   Новая цена: {updated_book['price']}")
    else:
        print(f"❌ Ошибка обновления: {response.text}")
    
    # 4. Получение списка всех аудиокниг
    print(f"\n4. Получение списка всех аудиокниг...")
    response = requests.get(f"{BASE_URL}/api/v1/audiobooks")
    print(f"Статус: {response.status_code}")
    
    if response.status_code == 200:
        books = response.json()
        print(f"✅ Получено {len(books)} аудиокниг")
        for book in books[:3]:  # Показываем первые 3
            print(f"   - {book['title']} (ID: {book['id']})")
    else:
        print(f"❌ Ошибка получения списка: {response.text}")
    
    # 5. Удаление аудиокниги
    print(f"\n5. Удаление аудиокниги с ID {book_id}...")
    response = requests.delete(f"{BASE_URL}/api/v1/audiobooks/{book_id}")
    print(f"Статус: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Аудиокнига удалена: {result['message']}")
    else:
        print(f"❌ Ошибка удаления: {response.text}")
    
    # 6. Проверка, что аудиокнига действительно удалена
    print(f"\n6. Проверка удаления аудиокниги с ID {book_id}...")
    response = requests.get(f"{BASE_URL}/api/v1/audiobooks/{book_id}")
    print(f"Статус: {response.status_code}")
    
    if response.status_code == 404:
        print("✅ Аудиокнига успешно удалена (получена ошибка 404)")
    else:
        print(f"❌ Аудиокнига не была удалена: {response.text}")
    
    print("\n" + "=" * 50)
    print("🏁 Тестирование завершено!")

def test_error_handling():
    """Тестирует обработку ошибок."""
    
    print("\n🧪 Тестирование обработки ошибок")
    print("=" * 50)
    
    # Тест получения несуществующей аудиокниги
    print("\n1. Попытка получения несуществующей аудиокниги...")
    response = requests.get(f"{BASE_URL}/api/v1/audiobooks/99999")
    print(f"Статус: {response.status_code}")
    
    if response.status_code == 404:
        print("✅ Правильно обработана ошибка 404")
    else:
        print(f"❌ Неожиданный статус: {response.status_code}")
    
    # Тест создания аудиокниги с несуществующим автором
    print("\n2. Попытка создания аудиокниги с несуществующим автором...")
    create_data = {
        "title": "Тестовая аудиокнига",
        "author_id": 99999,  # Несуществующий автор
        "price": "29.99"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/audiobooks", json=create_data)
    print(f"Статус: {response.status_code}")
    
    if response.status_code == 404:
        print("✅ Правильно обработана ошибка 404 для несуществующего автора")
    else:
        print(f"❌ Неожиданный статус: {response.status_code}")

if __name__ == "__main__":
    try:
        test_crud_operations()
        test_error_handling()
    except requests.exceptions.ConnectionError:
        print("❌ Ошибка подключения к сервису. Убедитесь, что сервис каталога запущен на порту 8001.")
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
