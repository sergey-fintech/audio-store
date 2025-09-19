# Prompts Manager Service

Сервис для управления промптами AI-системы Audio Store.

## Описание

Этот сервис отвечает за:
- Управление промптами для различных AI-сервисов
- Создание, обновление и получение промптов
- Инициализацию промптов по умолчанию
- RESTful API для работы с промптами

## Функциональность

### Промпты по умолчанию

При запуске сервиса автоматически создаются два промпта:

1. **recommendation_prompt** - для генерации рекомендаций аудиокниг
2. **description_prompt** - для генерации описаний аудиокниг

### API Endpoints

#### Основные операции
- `GET /prompts` - получить список всех промптов
- `GET /prompts/{prompt_id}` - получить промпт по ID
- `GET /prompts/name/{prompt_name}` - получить промпт по имени
- `POST /prompts` - создать новый промпт
- `PUT /prompts/{prompt_id}` - обновить промпт
- `DELETE /prompts/{prompt_id}` - удалить промпт

#### Управление состоянием
- `PUT /prompts/{prompt_id}/activate` - активировать промпт
- `PUT /prompts/{prompt_id}/deactivate` - деактивировать промпт

#### Служебные
- `GET /health` - проверка состояния сервиса
- `GET /prompts/initialize/defaults` - инициализировать промпты по умолчанию

## Запуск

### Установка зависимостей
```bash
pip install -r requirements.txt
```

### Запуск сервиса
```bash
python run_app.py
```

Сервис будет доступен по адресу: http://localhost:8006

### Документация API
- Swagger UI: http://localhost:8006/docs
- ReDoc: http://localhost:8006/redoc

## Структура данных

### Модель Prompt
```python
{
    "id": int,
    "name": str,           # Уникальное имя промпта
    "content": str,        # Содержимое промпта
    "description": str,    # Описание промпта (опционально)
    "is_active": str,      # Статус активности ("true"/"false")
    "created_at": datetime,
    "updated_at": datetime
}
```

## Примеры использования

### Создание промпта
```bash
curl -X POST "http://localhost:8006/prompts" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "custom_prompt",
       "content": "Ты - помощник по аудиокнигам...",
       "description": "Кастомный промпт для тестирования"
     }'
```

### Получение промпта по имени
```bash
curl "http://localhost:8006/prompts/name/recommendation_prompt"
```

### Обновление промпта
```bash
curl -X PUT "http://localhost:8006/prompts/1" \
     -H "Content-Type: application/json" \
     -d '{
       "content": "Обновленное содержимое промпта...",
       "is_active": "true"
     }'
```

## Интеграция с другими сервисами

Сервис использует ту же базу данных MySQL, что и другие микросервисы системы Audio Store. Промпты могут использоваться:

- **Recommender Service** - для генерации рекомендаций
- **Catalog Service** - для генерации описаний аудиокниг
- **Admin Panel** - для управления промптами через веб-интерфейс

## Технические детали

- **Framework**: FastAPI
- **Database**: MySQL с SQLAlchemy ORM
- **Port**: 8006
- **CORS**: Настроен для работы с фронтендом
- **Auto-reload**: Включен в режиме разработки
