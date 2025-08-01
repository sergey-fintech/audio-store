# Catalog Service API

FastAPI приложение для прикладного слоя домена "Каталог".

## Архитектура

Приложение построено по принципам DDD (Domain-Driven Design) и включает:

- **DTO схемы** (`schemas.py`) - Pydantic модели для валидации данных
- **Сервисы прикладного слоя** (`services.py`) - координация между API и доменными сервисами
- **API эндпоинты** (`app.py`) - REST API для работы с каталогом

## Запуск приложения

### Способ 1: Прямой запуск
```bash
cd services/catalog
python app.py
```

### Способ 2: Через uvicorn
```bash
cd services/catalog
uvicorn app:app --host 0.0.0.0 --port 8001 --reload
```

### Способ 3: Через скрипт
```bash
cd services/catalog
python run_app.py
```

## API Эндпоинты

### Основные эндпоинты
- `GET /` - Корневой эндпоинт
- `GET /health` - Проверка состояния сервиса

### API v1
- `GET /api/v1/audiobooks` - Получить список всех аудиокниг
- `GET /api/v1/audiobooks/{id}` - Получить аудиокнигу по ID
- `POST /api/v1/audiobooks` - Создать аудиокнигу
- `POST /api/v1/audiobooks/comprehensive` - Создать аудиокнигу с автором и категориями
- `POST /api/v1/audiobooks/search` - Поиск аудиокниг

### Авторы
- `GET /api/v1/authors` - Получить всех авторов
- `GET /api/v1/authors/{id}` - Получить автора по ID
- `POST /api/v1/authors` - Создать автора
- `GET /api/v1/authors/{id}/audiobooks` - Получить аудиокниги автора
- `GET /api/v1/authors/{id}/summary` - Получить сводку работ автора

### Категории
- `GET /api/v1/categories` - Получить все категории
- `GET /api/v1/categories/{id}` - Получить категорию по ID
- `POST /api/v1/categories` - Создать категорию
- `GET /api/v1/categories/{id}/audiobooks` - Получить аудиокниги категории
- `GET /api/v1/categories/{id}/analysis` - Получить анализ категории

### Статистика
- `GET /api/v1/catalog/statistics` - Получить статистику каталога

## Документация API

После запуска приложения документация доступна по адресам:
- Swagger UI: http://localhost:8001/api/docs
- ReDoc: http://localhost:8001/api/redoc
- OpenAPI JSON: http://localhost:8001/api/openapi.json

## Тестирование

### Проверка здоровья сервиса
```bash
curl http://localhost:8001/health
```

### Получение списка аудиокниг
```bash
curl http://localhost:8001/api/v1/audiobooks
```

### Создание автора
```bash
curl -X POST http://localhost:8001/api/v1/authors \
  -H "Content-Type: application/json" \
  -d '{"name": "Джордж Оруэлл"}'
```

### Создание аудиокниги
```bash
curl -X POST http://localhost:8001/api/v1/audiobooks/comprehensive \
  -H "Content-Type: application/json" \
  -d '{
    "title": "1984",
    "author_name": "Джордж Оруэлл",
    "price": 29.99,
    "description": "Классический роман-антиутопия",
    "category_names": ["Фантастика", "Классика"]
  }'
```

## Структура проекта

```
services/catalog/
├── app.py              # FastAPI приложение
├── schemas.py          # Pydantic DTO схемы
├── services.py         # Сервисы прикладного слоя
├── run_app.py          # Скрипт запуска
├── test_imports.py     # Тест импортов
└── README.md           # Документация
```

## Особенности реализации

1. **Чистая архитектура**: Разделение на слои (API, Application, Domain, Infrastructure)
2. **DTO схемы**: Строгая типизация и валидация данных
3. **Dependency Injection**: Использование FastAPI Depends для внедрения зависимостей
4. **Обработка ошибок**: Централизованная обработка исключений
5. **Документация**: Автоматическая генерация OpenAPI документации
6. **Пагинация**: Поддержка лимитов и смещений для больших списков
7. **Поиск и фильтрация**: Комплексный поиск с множественными фильтрами 