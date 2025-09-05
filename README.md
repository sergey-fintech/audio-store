# Audio Store - Доменная модель каталога аудиокниг

Этот проект представляет собой полную доменную модель для каталога аудиокниг, реализованную с использованием SQLAlchemy и следующих принципам Domain-Driven Design (DDD).

## Архитектура

Проект построен в соответствии с принципами DDD и включает следующие компоненты:

### Доменная модель (`database/`)
- **`models.py`** - Доменные сущности и агрегаты
- **`repositories.py`** - Репозитории для работы с агрегатами
- **`services.py`** - Доменные сервисы
- **`connection.py`** - Модуль подключения к базе данных
- **`examples.py`** - Примеры использования
- **`README.md`** - Документация по доменной модели

### Сервисы (`services/`)
- **`catalog/`** - FastAPI сервис каталога с полным API
  - `app.py` - Основное FastAPI приложение с эндпоинтами
  - `schemas.py` - Pydantic DTO схемы для валидации данных
  - `services.py` - Сервисы прикладного слоя
  - `main.py` - Устаревший API (для совместимости)

### Тесты (`tests/`)
- **`test_domain_models.py`** - Полный набор тестов для доменной модели

## Доменная модель

### Сущности

#### Author (Автор)
- Уникальный идентификатор
- Имя автора (уникальное)
- Связь один-ко-многим с Audiobook

#### Category (Категория)
- Уникальный идентификатор
- Название категории (уникальное)
- Связь многие-ко-многим с Audiobook

### Агрегат Audiobook (Корень агрегата)

#### Атрибуты
- Уникальный идентификатор
- Название аудиокниги
- Описание
- Цена (с валидацией)
- Ссылка на изображение обложки
- Связь с автором

#### Бизнес-методы
- `add_category(category)` - Добавление категории
- `remove_category(category)` - Удаление категории
- `update_price(new_price)` - Обновление цены с валидацией
- `get_categories_names()` - Получение списка названий категорий
- `has_category(category_name)` - Проверка принадлежности к категории
- `author_name` - Свойство для получения имени автора

## Репозитории

### AuthorRepository
- CRUD операции для авторов
- Поиск по имени

### CategoryRepository
- CRUD операции для категорий
- Поиск по названию

### AudiobookRepository
- CRUD операции для аудиокниг
- Поиск с фильтрацией
- Управление связями с категориями
- Пагинация

## Доменный сервис

### CatalogDomainService
- Создание аудиокниг с автоматическим созданием/поиском авторов и категорий
- Комплексный поиск с множественными фильтрами
- Статистика каталога
- Анализ авторов и категорий
- Валидация данных

## Веб-интерфейс

### Админ-панель
Полнофункциональная веб-панель для управления каталогом аудиокниг:

- **URL**: `http://localhost:8000/admin/admin.html`
- **Функции**: 
  - Просмотр всех аудиокниг в табличном виде
  - Добавление новых аудиокниг
  - Редактирование существующих записей
  - Удаление аудиокниг
  - Автоматическое создание авторов по имени
- **Технологии**: HTML5, CSS3, JavaScript (ES6+)
- **API**: Интеграция с REST API каталога

## API Endpoints

### Новый API v1 (рекомендуется)
Полный REST API с DTO схемами и валидацией данных:

#### Основные эндпоинты
- `GET /` - Корневой эндпоинт
- `GET /health` - Проверка состояния сервиса

#### API v1
- `GET /api/v1/audiobooks` - Получить список всех аудиокниг с полной информацией
- `GET /api/v1/audiobooks/{id}` - Получить аудиокнигу по ID
- `POST /api/v1/audiobooks` - Создать аудиокнигу
- `POST /api/v1/audiobooks/comprehensive` - Создать аудиокнигу с автором и категориями
- `POST /api/v1/audiobooks/search` - Поиск аудиокниг с фильтрами

#### Авторы
- `GET /api/v1/authors` - Получить всех авторов
- `GET /api/v1/authors/{id}` - Получить автора по ID
- `POST /api/v1/authors` - Создать автора
- `GET /api/v1/authors/{id}/audiobooks` - Получить аудиокниги автора
- `GET /api/v1/authors/{id}/summary` - Получить сводку работ автора

#### Категории
- `GET /api/v1/categories` - Получить все категории
- `GET /api/v1/categories/{id}` - Получить категорию по ID
- `POST /api/v1/categories` - Создать категорию
- `GET /api/v1/categories/{id}/audiobooks` - Получить аудиокниги категории
- `GET /api/v1/categories/{id}/analysis` - Получить анализ категории

#### Статистика
- `GET /api/v1/catalog/statistics` - Получить статистику каталога

### Устаревший API (для совместимости)
- `GET /authors` - Получить всех авторов
- `GET /authors/{author_id}` - Получить автора по ID
- `POST /authors` - Создать автора
- `GET /categories` - Получить все категории
- `GET /categories/{category_id}` - Получить категорию по ID
- `POST /categories` - Создать категорию
- `GET /audiobooks` - Получить все аудиокниги (с пагинацией)
- `GET /audiobooks/{audiobook_id}` - Получить аудиокнигу по ID
- `POST /audiobooks` - Создать аудиокнигу
- `GET /audiobooks/search` - Поиск аудиокниг
- `GET /audiobooks/author/{author_id}` - Аудиокниги по автору
- `GET /audiobooks/category/{category_id}` - Аудиокниги по категории

### Доменный сервис
- `GET /catalog/statistics` - Статистика каталога
- `GET /catalog/authors/{author_id}/summary` - Сводка работ автора
- `GET /catalog/categories/{category_id}/analysis` - Анализ категории
- `POST /catalog/audiobooks/comprehensive` - Создание с автором и категориями
- `GET /catalog/audiobooks/comprehensive-search` - Комплексный поиск

## Установка и запуск

### 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 2. Инициализация базы данных
```bash
# Создание таблиц
python init_db.py

# Создание таблиц с образцами данных
python init_db.py --sample-data

# Проверка состояния базы данных
python init_db.py --info --check
```

### 3. Запуск сервиса
### Новое приложение (рекомендуется)
```bash
cd services/catalog
python app.py
```

### Альтернативные способы запуска
```bash
# Через uvicorn
cd services/catalog
uvicorn app:app --host 0.0.0.0 --port 8001 --reload

# Через скрипт
cd services/catalog
python run_app.py

# Устаревший API
cd services/catalog
python main.py
```

Сервис будет доступен по адресу: http://localhost:8001

### Документация API
После запуска документация доступна по адресам:
- Swagger UI: http://localhost:8001/api/docs
- ReDoc: http://localhost:8001/api/redoc

### 4. Запуск тестов
```bash
pytest tests/test_domain_models.py -v
pytest tests/test_database_connection.py -v
```

### 5. Примеры использования
```bash
python database/examples.py
```

### 6. Команды для работы с базой данных

#### Инициализация базы данных
```bash
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

#### Проверка состояния
```bash
# Проверка подключения к БД
python init_db.py --check

# Получение информации о БД
python init_db.py --info
```

#### Создание образцов данных
```bash
# Создание БД с образцами данных
python init_db.py --sample-data

# Сброс и создание образцов данных
python init_db.py --reset --sample-data
```

## Принципы DDD в реализации

### 1. Агрегаты и их границы
- `Audiobook` является корнем агрегата
- Все изменения состояния происходят через методы агрегата
- Репозиторий работает только с корнем агрегата

### 2. Инкапсуляция бизнес-логики
- Валидация цены происходит внутри агрегата
- Управление категориями инкапсулировано в агрегате
- Доменный сервис содержит логику, работающую с несколькими агрегатами

### 3. Репозитории
- Инкапсулируют логику доступа к данным
- Предоставляют интерфейс для работы с агрегатами
- Обеспечивают целостность данных

### 4. Доменные сервисы
- Содержат бизнес-логику, не принадлежащую конкретному агрегату
- Координируют работу нескольких агрегатов
- Предоставляют сложные операции

## Структура базы данных

```sql
-- Таблица авторов
CREATE TABLE authors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME
);

-- Таблица категорий
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME
);

-- Таблица аудиокниг
CREATE TABLE audiobooks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    price NUMERIC(10, 2) NOT NULL,
    cover_image_url VARCHAR(500),
    author_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME,
    FOREIGN KEY (author_id) REFERENCES authors(id)
);

-- Таблица связи многие-ко-многим
CREATE TABLE audiobook_category (
    audiobook_id INTEGER,
    category_id INTEGER,
    PRIMARY KEY (audiobook_id, category_id),
    FOREIGN KEY (audiobook_id) REFERENCES audiobooks(id),
    FOREIGN KEY (category_id) REFERENCES categories(id)
);
```

## Документация API

После запуска сервиса документация API будет доступна по адресу:
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## Проверка состояния системы

### Проверка сервиса
```bash
# Проверка состояния сервиса
curl http://localhost:8001/health

# Проверка состояния БД через API
curl http://localhost:8001/catalog/statistics
```

### Проверка базы данных
```bash
# Проверка подключения к БД
python init_db.py --check

# Получение информации о БД
python init_db.py --info
```

## Тестирование

Проект включает полный набор тестов для всех компонентов доменной модели:

- Тесты сущностей (Author, Category)
- Тесты агрегата (Audiobook)
- Тесты репозиториев
- Тесты доменного сервиса
- Тесты бизнес-логики агрегата
- Тесты подключения к базе данных

Запуск тестов:
```bash
pytest tests/test_domain_models.py -v
pytest tests/test_database_connection.py -v
```

## Документация

- **Основная документация**: [README.md](README.md)
- **Команды для работы**: [COMMANDS.md](COMMANDS.md)
- **Документация доменной модели**: [database/README.md](database/README.md)

## Лицензия

MIT License
