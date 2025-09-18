#!/usr/bin/env python3
"""
Тестовый скрипт для проверки нового эндпоинта генерации описания
"""

import requests
import json
import time

# Конфигурация
RECOMMENDER_SERVICE_URL = "http://localhost:8005"
CATALOG_SERVICE_URL = "http://localhost:8002"

def test_description_generation():
    """Тестирует эндпоинт генерации описания"""
    
    print("🧪 Тестирование эндпоинта генерации описания")
    print("=" * 50)
    
    # 1. Проверяем доступность сервисов
    print("1️⃣ Проверка доступности сервисов...")
    
    try:
        # Проверяем recommender сервис
        response = requests.get(f"{RECOMMENDER_SERVICE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Recommender сервис доступен")
        else:
            print(f"❌ Recommender сервис недоступен: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Ошибка подключения к recommender сервису: {e}")
        return
    
    try:
        # Проверяем catalog сервис
        response = requests.get(f"{CATALOG_SERVICE_URL}/api/v1/audiobooks", timeout=5)
        if response.status_code == 200:
            print("✅ Catalog сервис доступен")
            audiobooks = response.json()
            if audiobooks:
                print(f"📚 Найдено {len(audiobooks)} аудиокниг")
            else:
                print("⚠️ Каталог пуст")
                return
        else:
            print(f"❌ Catalog сервис недоступен: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Ошибка подключения к catalog сервису: {e}")
        return
    
    # 2. Выбираем первую книгу для тестирования
    print("\n2️⃣ Выбор книги для тестирования...")
    first_book = audiobooks[0]
    book_id = first_book['id']
    book_title = first_book['title']
    current_description = first_book.get('description', 'Отсутствует')
    
    print(f"📖 Выбрана книга: {book_title} (ID: {book_id})")
    print(f"📝 Текущее описание: {current_description[:100]}..." if len(current_description) > 100 else f"📝 Текущее описание: {current_description}")
    
    # 3. Тестируем генерацию описания
    print(f"\n3️⃣ Генерация описания для книги {book_id}...")
    
    try:
        url = f"{RECOMMENDER_SERVICE_URL}/api/v1/recommendations/generate-description/{book_id}"
        payload = {
            "model": "gemini-pro"
        }
        
        print(f"🔗 URL: {url}")
        print(f"📤 Payload: {json.dumps(payload, ensure_ascii=False, indent=2)}")
        
        response = requests.post(url, json=payload, timeout=60)
        
        print(f"📡 Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Генерация описания успешна!")
            print(f"📝 Сгенерированное описание:")
            print("-" * 50)
            print(result['generated_description'])
            print("-" * 50)
            print(f"🤖 Модель: {result['model_alias']} -> {result['model']}")
            print(f"✅ Успех: {result['success']}")
            
            # 4. Проверяем, что описание обновилось в catalog
            print(f"\n4️⃣ Проверка обновления в catalog сервисе...")
            time.sleep(2)  # Небольшая задержка
            
            check_response = requests.get(f"{CATALOG_SERVICE_URL}/api/v1/audiobooks/{book_id}")
            if check_response.status_code == 200:
                updated_book = check_response.json()
                updated_description = updated_book.get('description', '')
                print(f"📝 Обновленное описание в catalog:")
                print("-" * 50)
                print(updated_description)
                print("-" * 50)
                
                if updated_description == result['generated_description']:
                    print("✅ Описание успешно обновлено в catalog сервисе!")
                else:
                    print("⚠️ Описание в catalog отличается от сгенерированного")
            else:
                print(f"❌ Ошибка при проверке обновления: {check_response.status_code}")
                
        else:
            print(f"❌ Ошибка генерации описания: {response.status_code}")
            print(f"📝 Ответ: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Таймаут при генерации описания (60 секунд)")
    except Exception as e:
        print(f"❌ Ошибка при генерации описания: {e}")
    
    print("\n🎯 Тестирование завершено!")

if __name__ == "__main__":
    test_description_generation()
