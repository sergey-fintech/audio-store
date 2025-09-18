# AI Recommender Service

## Описание

AI Recommender Service - это Core Domain микросервис для генерации персонализированных рекомендаций аудиокниг с использованием LLM (Large Language Models).

## Архитектура

Этот сервис является **ограниченным контекстом** в рамках Domain-Driven Design и отвечает за:

- Анализ каталога аудиокниг
- Генерацию персонализированных рекомендаций
- Взаимодействие с LLM через OpenRouter API
- Интеграцию с Catalog Service

## Установка и запуск

### 1. Установка зависимостей

```bash
cd services/recommender
pip install -r requirements.txt
```

### 2. Настройка переменных окружения

**ВАЖНО**: Для работы сервиса необходим API ключ OpenRouter.

#### Получение API ключа:
1. Зарегистрируйтесь на https://openrouter.ai/
2. Создайте API ключ в личном кабинете
3. Установите переменную окружения:

```bash
# Windows PowerShell
$env:OPENROUTER_API_KEY="your_openrouter_api_key_here"

# Windows CMD
set OPENROUTER_API_KEY=your_openrouter_api_key_here

# Linux/Mac
export OPENROUTER_API_KEY="your_openrouter_api_key_here"
```

#### Альтернативно - создайте файл .env:
```bash
# Скопируйте env_template.txt в .env и заполните значения
cp env_template.txt .env
# Затем отредактируйте .env файл
```

### 3. Запуск сервиса

#### Автоматическая настройка и запуск:
```bash
python setup_and_run.py
```

#### Ручной запуск:
```bash
python run_app.py
```

Сервис будет доступен по адресу: http://localhost:8005

### 4. Проверка работы

После запуска проверьте:
- Health check: http://localhost:8005/health
- API документация: http://localhost:8005/docs
- Тест сервиса: `python test_new_api.py`

## API Endpoints

### POST /api/v1/recommendations/generate

Основной эндпоинт для генерации рекомендаций.

**Запрос:**
```json
{
  "prompt": "Рекомендуй мне интересные аудиокниги для вечернего чтения"
}
```

**Ответ:**
```json
{
  "recommendations": "Полный ответ от LLM с рекомендациями и обоснованием",
  "model": "mistralai/mistral-7b-instruct",
  "total_books_analyzed": 25
}
```

### Примеры запросов:

```json
// Запрос по жанру
{
  "prompt": "Ищу детективы и триллеры, не дороже 300 рублей"
}

// Запрос по автору
{
  "prompt": "Хочу послушать что-то от классических авторов русской литературы"
}

// Запрос для путешествия
{
  "prompt": "Нужны короткие аудиокниги для поездки в поезде, 2-3 часа"
}
```

### GET /health

Проверка состояния сервиса.

### GET /api/v1/recommendations/catalog-info

Получение информации о каталоге для отладки.

## Взаимодействие с другими сервисами

Сервис взаимодействует с:
- **Catalog Service** (http://localhost:8002) - для получения каталога аудиокниг
- **OpenRouter API** - для работы с LLM (Mistral 7B)

## Core Domain Логика

### Системный промпт

Сервис использует системный промпт, который является интеллектуальной собственностью и включает:

- Полный каталог аудиокниг в JSON формате
- Задачу пользователя из промпта
- Инструкции по анализу и рекомендациям
- Форматирование ответа

### Алгоритм работы

1. **Получение данных**: GET-запрос к Catalog Service (Anti-Corruption Layer)
2. **Создание промпта**: Формирование системного промпта с каталогом и задачей пользователя
3. **LLM анализ**: Отправка запроса к Mistral 7B через OpenRouter
4. **Возврат результата**: Ответ от модели "как есть"

## Технические детали

- **Framework**: FastAPI
- **LLM Provider**: OpenRouter (mistralai/mistral-7b-instruct)
- **HTTP Client**: httpx
- **Port**: 8005
- **API**: Упрощенный с одним полем `prompt`

## Мониторинг и отладка

- API документация: http://localhost:8005/docs
- Health check: http://localhost:8005/health
- Catalog info: http://localhost:8005/api/v1/recommendations/catalog-info

## Требования

- Python 3.8+
- OpenRouter API ключ
- Доступ к Catalog Service (порт 8002)
