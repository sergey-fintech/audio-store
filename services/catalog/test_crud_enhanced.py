"""
Улучшенный тестовый файл для проверки CRUD операций с аудиокнигами.
Сначала проверяет существующие данные, затем тестирует CRUD операции.
"""

import requests
import json
from decimal import Decimal

# Базовый URL сервиса каталога
BASE_URL = "http://localhost:8002"

def check_existing_data():
    """Проверяет существующие данные в базе."""
    
    print("🔍 Проверка существующих данных")
    print("=" * 50)
    
    # Проверяем авторов
    print("\n1. Проверка авторов...")
    response = requests.get(f"{BASE_URL}/authors")
    if response.status_code == 200:
        authors = response.json()
        print(f"✅ Найдено {len(authors)} авторов:")
        for author in authors[:5]:  # Показываем первые 5
            print(f"   - ID: {author['id']}, Имя: {author['name']}")
        return authors[0]['id'] if authors else None
    else:
        print(f"❌ Ошибка получения авторов: {response.status_code}")
        return None
    
    # Проверяем категории
    print("\n2. Проверка категорий...")
    response = requests.get(f"{BASE_URL}/categories")
    if response.status_code == 200:
        categories = response.json()
        print(f"✅ Найдено {len(categories)} категорий:")
        for category in categories[:5]:  # Показываем первые 5
            print(f"   - ID: {category['id']}, Название: {category['name']}")
        return categories[0]['id'] if categories else None
    else:
        print(f"❌ Ошибка получения категорий: {response.status_code}")
        return None

def test_crud_operations():
    """Тестирует все CRUD операции для аудиокниг."""
    
    print("\n🧪 Тестирование CRUD операций для аудиокниг")
    print("=" * 50)
    
    # Получаем существующие данные
    authors_response = requests.get(f"{BASE_URL}/authors")
    categories_response = requests.get(f"{BASE_URL}/categories")
    
    if authors_response.status_code != 200 or categories_response.status_code != 200:
        print("❌ Не удалось получить данные авторов или категорий")
        return
    
    authors = authors_response.json()
    categories = categories_response.json()
    
    if not authors:
        print("❌ Нет авторов в базе данных")
        return
    
    if not categories:
        print("❌ Нет категорий в базе данных")
        return
    
    author_id = authors[0]['id']
    category_id = categories[0]['id']
    
    print(f"📝 Используем автора: {authors[0]['name']} (ID: {author_id})")
    print(f"📝 Используем категорию: {categories[0]['name']} (ID: {category_id})")
    
    # 1. Создание аудиокниги
    print(f"\n1. Создание новой аудиокниги...")
    create_data = {
        "title": "Тестовая аудиокнига CRUD",
        "author_id": author_id,
        "price": "29.99",
        "description": "Описание тестовой аудиокниги для проверки CRUD операций",
        "cover_image_url": "https://example.com/test-cover.jpg",
        "category_ids": [category_id]
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/audiobooks", json=create_data)
    print(f"Статус: {response.status_code}")
    
    if response.status_code == 201 or response.status_code == 200:
        created_book = response.json()
        book_id = created_book["id"]
        print(f"✅ Аудиокнига создана с ID: {book_id}")
        print(f"   Название: {created_book['title']}")
        print(f"   Цена: {created_book['price']}")
        print(f"   Автор: {created_book['author']['name'] if created_book['author'] else 'Не указан'}")
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
        print(f"   Категории: {len(book['categories'])} шт.")
    else:
        print(f"❌ Ошибка получения: {response.text}")
    
    # 3. Обновление аудиокниги
    print(f"\n3. Обновление аудиокниги с ID {book_id}...")
    update_data = {
        "title": "Обновленная тестовая аудиокнига CRUD",
        "price": "39.99",
        "description": "Обновленное описание для тестовой аудиокниги"
    }
    
    response = requests.put(f"{BASE_URL}/api/v1/audiobooks/{book_id}", json=update_data)
    print(f"Статус: {response.status_code}")
    
    if response.status_code == 200:
        updated_book = response.json()
        print(f"✅ Аудиокнига обновлена:")
        print(f"   Новое название: {updated_book['title']}")
        print(f"   Новая цена: {updated_book['price']}")
        print(f"   Новое описание: {updated_book['description']}")
    else:
        print(f"❌ Ошибка обновления: {response.text}")
    
    # 4. Получение списка всех аудиокниг
    print(f"\n4. Получение списка всех аудиокниг...")
    response = requests.get(f"{BASE_URL}/api/v1/audiobooks")
    print(f"Статус: {response.status_code}")
    
    if response.status_code == 200:
        books = response.json()
        print(f"✅ Получено {len(books)} аудиокниг")
        # Ищем нашу тестовую книгу
        test_book = next((book for book in books if book['title'] == "Обновленная тестовая аудиокнига CRUD"), None)
        if test_book:
            print(f"   ✅ Наша тестовая книга найдена в списке (ID: {test_book['id']})")
        else:
            print(f"   ⚠️ Наша тестовая книга не найдена в списке")
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
    
    # Тест обновления несуществующей аудиокниги
    print("\n3. Попытка обновления несуществующей аудиокниги...")
    update_data = {
        "title": "Обновленное название",
        "price": "39.99"
    }
    
    response = requests.put(f"{BASE_URL}/api/v1/audiobooks/99999", json=update_data)
    print(f"Статус: {response.status_code}")
    
    if response.status_code == 404:
        print("✅ Правильно обработана ошибка 404 для несуществующей аудиокниги")
    else:
        print(f"❌ Неожиданный статус: {response.status_code}")
    
    # Тест удаления несуществующей аудиокниги
    print("\n4. Попытка удаления несуществующей аудиокниги...")
    response = requests.delete(f"{BASE_URL}/api/v1/audiobooks/99999")
    print(f"Статус: {response.status_code}")
    
    if response.status_code == 404:
        print("✅ Правильно обработана ошибка 404 для удаления несуществующей аудиокниги")
    else:
        print(f"❌ Неожиданный статус: {response.status_code}")

def test_existing_audiobooks():
    """Тестирует работу с существующими аудиокнигами."""
    
    print("\n📚 Тестирование работы с существующими аудиокнигами")
    print("=" * 50)
    
    # Получаем список всех аудиокниг
    response = requests.get(f"{BASE_URL}/api/v1/audiobooks")
    if response.status_code == 200:
        books = response.json()
        print(f"✅ Найдено {len(books)} аудиокниг в базе данных")
        
        if books:
            # Тестируем получение первой аудиокниги
            first_book = books[0]
            book_id = first_book['id']
            
            print(f"\n📖 Тестируем получение аудиокниги с ID {book_id}...")
            response = requests.get(f"{BASE_URL}/api/v1/audiobooks/{book_id}")
            
            if response.status_code == 200:
                book = response.json()
                print(f"✅ Аудиокнига получена:")
                print(f"   Название: {book['title']}")
                print(f"   Автор: {book['author']['name'] if book['author'] else 'Не указан'}")
                print(f"   Цена: {book['price']}")
                print(f"   Категории: {len(book['categories'])} шт.")
            else:
                print(f"❌ Ошибка получения: {response.status_code}")
        else:
            print("⚠️ В базе данных нет аудиокниг")
    else:
        print(f"❌ Ошибка получения списка аудиокниг: {response.status_code}")

if __name__ == "__main__":
    try:
        check_existing_data()
        test_existing_audiobooks()
        test_crud_operations()
        test_error_handling()
    except requests.exceptions.ConnectionError:
        print("❌ Ошибка подключения к сервису. Убедитесь, что сервис каталога запущен на порту 8001.")
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
