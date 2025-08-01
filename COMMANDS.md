# Команды для работы с Audio Store

## Установка и настройка

### 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 2. Инициализация базы данных
```bash
# Полная настройка (удаление дублирующих файлов + создание тестовых данных)
python setup_database.py

# Создание таблиц
python init_db.py

# Создание таблиц с образцами данных
python init_db.py --sample-data

# Проверка состояния базы данных
python init_db.py --info --check

# Полный сброс базы данных (удаление всех данных)
python init_db.py --reset

# Комбинированные операции
python init_db.py --reset --sample-data --info
```

## Запуск сервисов

### 3. Запуск сервиса каталога
```bash
# Новое приложение (рекомендуется)
cd services/catalog
python app.py

# Альтернативные способы запуска
cd services/catalog
uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# Устаревший API
cd services/catalog
python main.py
```

Сервис будет доступен по адресу: http://localhost:8000
Документация API: http://localhost:8000/api/docs

### 4. Запуск микросервиса "Корзина"
```bash
# Запуск сервиса корзины
cd services/cart
python run_app.py

# Альтернативный способ запуска
cd services/cart
python main.py

# Демонстрация работы сервиса
cd services/cart
python demo.py
```

Сервис будет доступен по адресу: http://localhost:8001
Документация API: http://localhost:8001/docs

## Тестирование

### 4. Запуск тестов
```bash
# Тесты доменной модели
pytest tests/test_domain_models.py -v

# Тесты подключения к БД
pytest tests/test_database_connection.py -v

# Все тесты
pytest tests/ -v
```

### 5. Примеры использования
```bash
python database/examples.py
```

## Проверка состояния

### 6. Проверка сервиса
```bash
# Проверка состояния сервиса
curl http://localhost:8001/health

# Проверка состояния БД через API
curl http://localhost:8001/catalog/statistics
```

### 7. Проверка базы данных
```bash
# Проверка подключения к БД
python init_db.py --check

# Получение информации о БД
python init_db.py --info
```

## Работа с данными

### 8. Создание образцов данных
```bash
# Создание БД с образцами данных
python init_db.py --sample-data

# Сброс и создание образцов данных
python init_db.py --reset --sample-data
```

### 9. Сброс данных
```bash
# Полный сброс БД (удаление всех данных)
python init_db.py --reset
```

## API Endpoints

### Новый API v1 (рекомендуется)
```bash
# Получить список всех аудиокниг с полной информацией
curl http://localhost:8000/api/v1/audiobooks

# Получить аудиокнигу по ID
curl http://localhost:8000/api/v1/audiobooks/1

# Создать автора
curl -X POST http://localhost:8000/api/v1/authors \
  -H "Content-Type: application/json" \
  -d '{"name": "Джордж Оруэлл"}'

# Создать аудиокнигу с автором и категориями
curl -X POST http://localhost:8000/api/v1/audiobooks/comprehensive \
  -H "Content-Type: application/json" \
  -d '{
    "title": "1984",
    "author_name": "Джордж Оруэлл",
    "price": 29.99,
    "description": "Классический роман-антиутопия",
    "category_names": ["Фантастика", "Классика"]
  }'

# Поиск аудиокниг
curl -X POST http://localhost:8000/api/v1/audiobooks/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "фантастика",
    "min_price": 20.0,
    "max_price": 50.0,
    "limit": 10
  }'

# Статистика каталога
curl http://localhost:8000/api/v1/catalog/statistics
```

### API микросервиса "Корзина"
```bash
# Расчет стоимости корзины
curl -X POST http://localhost:8001/api/v1/cart/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"audiobook_id": 1, "quantity": 2},
      {"audiobook_id": 2, "quantity": 1},
      {"audiobook_id": 3, "quantity": 3}
    ]
  }'

# Проверка состояния сервиса корзины
curl http://localhost:8001/health
```

### Устаревший API (для совместимости)
```bash
# Получить всех авторов
curl http://localhost:8001/authors

# Получить автора по ID
curl http://localhost:8001/authors/1

# Создать автора
curl -X POST "http://localhost:8001/authors?name=Новый%20Автор"
```

### Категории
```bash
# Получить все категории
curl http://localhost:8001/categories

# Получить категорию по ID
curl http://localhost:8001/categories/1

# Создать категорию
curl -X POST "http://localhost:8001/categories?name=Новая%20Категория"
```

### Аудиокниги
```bash
# Получить все аудиокниги
curl http://localhost:8001/audiobooks

# Получить аудиокнигу по ID
curl http://localhost:8001/audiobooks/1

# Поиск аудиокниг
curl "http://localhost:8001/audiobooks/search?query=фэнтези"

# Аудиокниги по автору
curl http://localhost:8001/audiobooks/author/1

# Аудиокниги по категории
curl http://localhost:8001/audiobooks/category/1
```

### Доменный сервис
```bash
# Статистика каталога
curl http://localhost:8001/catalog/statistics

# Сводка работ автора
curl http://localhost:8001/catalog/authors/1/summary

# Анализ категории
curl http://localhost:8001/catalog/categories/1/analysis

# Комплексный поиск
curl "http://localhost:8001/catalog/audiobooks/comprehensive-search?query=фэнтези&min_price=20&max_price=50"
```

## Документация

### 10. Документация API
- Swagger UI: http://localhost:8001/api/docs
- ReDoc: http://localhost:8001/api/redoc
- OpenAPI JSON: http://localhost:8001/api/openapi.json

### 11. Документация проекта
- Основная документация: [README.md](README.md)
- Документация доменной модели: [database/README.md](database/README.md)

## Отладка

### 12. Логирование
```bash
# Запуск с подробным логированием
cd services/catalog
python main.py --log-level DEBUG
```

### 13. Проверка файлов БД
```bash
# Проверка размера файла БД
ls -la audio_store.db

# Проверка содержимого БД (если установлен sqlite3)
sqlite3 audio_store.db ".tables"
sqlite3 audio_store.db "SELECT * FROM authors;"
```

## Быстрый старт

Для быстрого запуска проекта выполните:

```bash
# 1. Установка зависимостей
pip install -r requirements.txt

# 2. Инициализация БД с образцами данных
python init_db.py --sample-data

# 3. Запуск микросервиса "Каталог"
cd services/catalog
python main.py

# 4. Запуск микросервиса "Корзина" (в новом терминале)
cd services/cart
python run_app.py

# 5. Проверка работы
curl http://localhost:8000/health  # Каталог
curl http://localhost:8001/health  # Корзина

# 6. Демонстрация работы корзины
cd services/cart
python demo.py
```

## Очистка

### 14. Очистка проекта
```bash
# Удаление файла БД
rm audio_store.db

# Удаление кэша Python
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -name "*.pyc" -delete
``` 