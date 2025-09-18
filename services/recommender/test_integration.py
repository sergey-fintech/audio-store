"""
Основной тест интеграции AI Recommender Service с каталогом
"""

import requests
import json

def test_catalog_integration():
    """Тест интеграции с каталогом и LLM"""
    
    print("🤖 Тест интеграции AI Recommender Service")
    print("=" * 50)
    
    # 1. Проверяем доступность сервиса
    try:
        health_response = requests.get("http://localhost:8005/health")
        if health_response.status_code == 200:
            health_data = health_response.json()
            print("✅ Сервис доступен")
            print(f"   API Key configured: {health_data.get('api_key_configured', False)}")
            print(f"   API Key length: {health_data.get('api_key_length', 0)}")
        else:
            print("❌ Сервис недоступен")
            return
    except Exception as e:
        print(f"❌ Ошибка подключения к сервису: {e}")
        return
    
    # 2. Получаем список доступных моделей
    try:
        models_response = requests.get("http://localhost:8005/api/v1/models")
        if models_response.status_code == 200:
            models_data = models_response.json()
            print(f"\n📋 Доступные модели: {len(models_data['available_models'])}")
            for alias, full_name in models_data["available_models"].items():
                print(f"   {alias}: {full_name}")
        else:
            print("❌ Не удалось получить список моделей")
            return
    except Exception as e:
        print(f"❌ Ошибка получения моделей: {e}")
        return
    
    # 3. Тестируем интеграцию с каталогом и LLM
    test_cases = [
        {
            "prompt": "Рекомендуй мне лучшие книги из каталога",
            "model": "gemini-pro",
            "description": "Общий запрос"
        },
        {
            "prompt": "Хочу послушать фантастику, что посоветуешь?",
            "model": "gemini-flash", 
            "description": "Запрос по жанру"
        },
        {
            "prompt": "Ищу недорогие аудиокниги до 30 рублей",
            "model": "claude-3",
            "description": "Запрос по цене"
        }
    ]
    
    print(f"\n🧪 Тестируем {len(test_cases)} сценариев:")
    print("-" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['description']}")
        print(f"   Модель: {test_case['model']}")
        print(f"   Запрос: {test_case['prompt']}")
        
        try:
            response = requests.post(
                "http://localhost:8005/api/v1/recommendations/generate",
                json={
                    "prompt": test_case["prompt"],
                    "model": test_case["model"]
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                print("   ✅ Успешно!")
                print(f"   🤖 Модель: {result.get('model', 'Не указана')}")
                print(f"   📚 Проанализировано книг: {result.get('total_books_analyzed', 'Не указано')}")
                
                recommendations = result.get('recommendations', '')
                print(f"   💬 Ответ (первые 100 символов):")
                print(f"   {recommendations[:100]}...")
                
            else:
                print(f"   ❌ Ошибка: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
    
    print(f"\n🏁 Тестирование завершено")
    print("=" * 50)

if __name__ == "__main__":
    test_catalog_integration()

