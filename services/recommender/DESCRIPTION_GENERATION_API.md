# API Генерации Описаний - Оркестратор

## Обзор

Новый эндпоинт `/api/v1/recommendations/generate-description/{product_id}` реализует паттерн **Оркестратор** для процесса AI-генерации описаний аудиокниг.

## Архитектура

Этот эндпоинт координирует взаимодействие между несколькими ограниченными контекстами:

1. **Catalog Service** - получение данных книги и обновление описания
2. **AI Recommender Service** - генерация описания с помощью LLM
3. **External LLM** (через OpenRouter) - создание контента

## Эндпоинт

### POST `/api/v1/recommendations/generate-description/{product_id}`

**Описание:** Оркестратор для генерации описания аудиокниги с помощью AI

**Параметры:**
- `product_id` (path) - ID аудиокниги в каталоге

**Тело запроса:**
```json
{
  "model": "gemini-pro"  // Опционально, по умолчанию "gemini-pro"
}
```

**Доступные модели:**
- `gemini-pro` - Google Gemini Pro 1.5
- `gemini-flash` - Google Gemini Flash 1.5 8B
- `claude-3` - Anthropic Claude 3.5 Sonnet
- `gpt-4` - OpenAI GPT-4 Turbo
- `llama-3` - Meta Llama 3 8B Instruct

**Ответ:**
```json
{
  "product_id": 1,
  "generated_description": "Привлекательное описание аудиокниги...",
  "model": "google/gemini-pro-1.5",
  "model_alias": "gemini-pro",
  "success": true
}
```

## Процесс Оркестрации

### Шаг 1: Получение данных книги
- **Действие:** GET запрос к `catalog` сервису
- **URL:** `http://localhost:8002/api/v1/audiobooks/{product_id}`
- **Цель:** Получить метаданные книги (название, автор, категории, цена, текущее описание)

### Шаг 2: Создание промпта
- **Действие:** Формирование системного промпта для LLM
- **Логика:** Использование Core Domain знаний для создания эффективного промпта
- **Входные данные:** Метаданные книги
- **Выходные данные:** Структурированный промпт для генерации описания

### Шаг 3: Генерация описания
- **Действие:** Вызов LLM через OpenRouter API
- **Модель:** Выбранная пользователем или по умолчанию
- **Параметры:** 
  - `max_tokens`: 500
  - `temperature`: 0.7
- **Результат:** Сгенерированное описание на русском языке

### Шаг 4: Обновление каталога
- **Действие:** PUT запрос к `catalog` сервису
- **URL:** `http://localhost:8002/api/v1/audiobooks/{product_id}`
- **Payload:** `{"description": "сгенерированное_описание"}` (схема AudiobookUpdate)
- **Цель:** Сохранить новое описание в базе данных

## Обработка Ошибок

### HTTP Коды Ошибок

- **404** - Аудиокнига не найдена
- **503** - Catalog сервис недоступен
- **500** - Ошибка LLM или внутренняя ошибка

### Типы Ошибок

1. **Ошибки подключения к catalog сервису**
   - Таймаут (10 секунд)
   - Сетевые ошибки
   - HTTP ошибки

2. **Ошибки LLM**
   - Неверный API ключ
   - Превышение лимитов
   - Ошибки модели

3. **Ошибки обновления**
   - Ошибки валидации
   - Проблемы с базой данных

## Примеры Использования

### cURL
```bash
curl -X POST "http://localhost:8005/api/v1/recommendations/generate-description/1" \
  -H "Content-Type: application/json" \
  -d '{"model": "gemini-pro"}'
```

### Python
```python
import requests

response = requests.post(
    "http://localhost:8005/api/v1/recommendations/generate-description/1",
    json={"model": "gemini-pro"}
)

if response.status_code == 200:
    result = response.json()
    print(f"Описание: {result['generated_description']}")
else:
    print(f"Ошибка: {response.status_code}")
```

## Тестирование

Запустите тестовый скрипт:
```bash
cd services/recommender
python test_description_generation.py
```

## Требования

1. **Catalog Service** должен быть запущен на порту 8002
2. **Recommender Service** должен быть запущен на порту 8005
3. **OPENROUTER_API_KEY** должен быть настроен в переменных окружения
4. В каталоге должны быть аудиокниги для тестирования

## Логирование

Сервис выводит подробные логи процесса оркестрации:
- 🎯 Начало оркестрации
- 📖 Получение данных книги
- 🤖 Создание промпта
- ⚡ Генерация описания
- 🔄 Обновление в catalog
- 🎉 Успешное завершение
- ❌ Ошибки на каждом этапе
