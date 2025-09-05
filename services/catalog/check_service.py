"""
Простой скрипт для проверки доступности сервиса каталога.
"""

import requests
import json

BASE_URL = "http://localhost:8002"

def check_service():
    """Проверяет доступность сервиса и его эндпоинтов."""
    
    print("🔍 Проверка доступности сервиса каталога")
    print("=" * 50)
    
    # Проверяем корневой эндпоинт
    print("\n1. Проверка корневого эндпоинта...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"Статус: {response.status_code}")
        if response.status_code == 200:
            print(f"Ответ: {response.json()}")
        else:
            print(f"Ответ: {response.text}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    # Проверяем health check
    print("\n2. Проверка health check...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"Статус: {response.status_code}")
        if response.status_code == 200:
            print(f"Ответ: {response.json()}")
        else:
            print(f"Ответ: {response.text}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    # Проверяем эндпоинт аудиокниг
    print("\n3. Проверка эндпоинта аудиокниг...")
    try:
        response = requests.get(f"{BASE_URL}/audiobooks", timeout=5)
        print(f"Статус: {response.status_code}")
        if response.status_code == 200:
            books = response.json()
            print(f"Найдено {len(books)} аудиокниг")
            if books:
                print(f"Первая книга: {books[0]['title']}")
        else:
            print(f"Ответ: {response.text}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    # Проверяем эндпоинт авторов
    print("\n4. Проверка эндпоинта авторов...")
    try:
        response = requests.get(f"{BASE_URL}/authors", timeout=5)
        print(f"Статус: {response.status_code}")
        if response.status_code == 200:
            authors = response.json()
            print(f"Найдено {len(authors)} авторов")
            if authors:
                print(f"Первый автор: {authors[0]['name']}")
        else:
            print(f"Ответ: {response.text}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    # Проверяем эндпоинт категорий
    print("\n5. Проверка эндпоинта категорий...")
    try:
        response = requests.get(f"{BASE_URL}/categories", timeout=5)
        print(f"Статус: {response.status_code}")
        if response.status_code == 200:
            categories = response.json()
            print(f"Найдено {len(categories)} категорий")
            if categories:
                print(f"Первая категория: {categories[0]['name']}")
        else:
            print(f"Ответ: {response.text}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    # Проверяем API v1 эндпоинты
    print("\n6. Проверка API v1 эндпоинтов...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/audiobooks", timeout=5)
        print(f"API v1 аудиокниги - Статус: {response.status_code}")
        if response.status_code == 200:
            books = response.json()
            print(f"Найдено {len(books)} аудиокниг через API v1")
        else:
            print(f"Ответ: {response.text}")
    except Exception as e:
        print(f"❌ Ошибка API v1: {e}")

if __name__ == "__main__":
    check_service()
