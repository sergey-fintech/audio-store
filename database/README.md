# Доменная модель каталога аудиокниг

Этот документ описывает полную доменную модель для домена "Каталог" аудиокниг, реализованную с использованием SQLAlchemy и следующих принципам Domain-Driven Design (DDD).

## Архитектура

Доменная модель построена в соответствии с принципами DDD и включает следующие компоненты:

### 1. Сущности (Entities)

#### Author (Автор)
- **Роль**: Сущность, представляющая автора аудиокниг
- **Атрибуты**:
  - `id`: Уникальный идентификатор
  - `name`: Имя автора (уникальное)
  - `created_at`, `updated_at`: Метаданные времени
- **Связи**: Один-ко-многим с Audiobook

#### Category (Категория)
- **Роль**: Сущность, представляющая категорию/жанр аудиокниг
- **Атрибуты**:
  - `id`: Уникальный идентификатор
  - `name`: Название категории (уникальное)
  - `created_at`, `updated_at`: Метаданные времени
- **Связи**: Многие-ко-многим с Audiobook

### 2. Агрегат (Aggregate)

#### Audiobook (Аудиокнига) - Корень агрегата
- **Роль**: Корневая сущность агрегата, инкапсулирующая бизнес-логику
- **Атрибуты**:
  - `id`: Уникальный идентификатор
  - `title`: Название аудиокниги
  - `description`: Описание
  - `price`: Цена (Numeric(10, 2))
  - `cover_image_url`: Ссылка на изображение обложки
  - `author_id`: Внешний ключ к Author
  - `created_at`, `updated_at`: Метаданные времени
- **Связи**:
  - Многие-к-одному с Author
  - Многие-ко-многим с Category через таблицу `audiobook_category`

## Бизнес-логика агрегата

Агрегат `Audiobook` содержит следующие бизнес-методы:

### Методы управления категориями
- `add_category(category)`: Добавляет категорию к аудиокниге
- `remove_category(category)`: Удаляет категорию из аудиокниги
- `get_categories_names()`: Возвращает список названий категорий
- `has_category(category_name)`: Проверяет принадлежность к категории

### Методы управления ценой
- `update_price(new_price)`: Обновляет цену с валидацией (не может быть отрицательной)

### Свойства
- `author_name`: Возвращает имя автора или "Unknown Author"

## Репозитории

### AuthorRepository
Предоставляет интерфейс для работы с сущностью Author:
- `create(name)`: Создание автора
- `get_by_id(id)`: Получение по ID
- `get_by_name(name)`: Получение по имени
- `get_all()`: Получение всех авторов
- `update(id, name)`: Обновление
- `delete(id)`: Удаление

### CategoryRepository
Предоставляет интерфейс для работы с сущностью Category:
- `create(name)`: Создание категории
- `get_by_id(id)`: Получение по ID
- `get_by_name(name)`: Получение по названию
- `get_all()`: Получение всех категорий
- `update(id, name)`: Обновление
- `delete(id)`: Удаление

### AudiobookRepository
Основной репозиторий для работы с агрегатом Audiobook:
- `create(title, author_id, price, description, cover_image_url)`: Создание аудиокниги
- `get_by_id(id)`: Получение с загруженными связями
- `get_all(limit, offset)`: Получение с пагинацией
- `get_by_author(author_id)`: Получение по автору
- `get_by_category(category_id)`: Получение по категории
- `search(query)`: Поиск по названию и описанию
- `update(id, **kwargs)`: Обновление
- `delete(id)`: Удаление
- `add_category(audiobook_id, category_id)`: Добавление категории
- `remove_category(audiobook_id, category_id)`: Удаление категории

## Доменный сервис

### CatalogDomainService
Содержит бизнес-логику, которая не принадлежит конкретному агрегату:

#### Методы создания и управления
- `create_audiobook_with_author_and_categories()`: Создание аудиокниги с автоматическим созданием/поиском автора и категорий

#### Методы анализа и статистики
- `get_catalog_statistics()`: Получение статистики каталога
- `get_author_works_summary(author_id)`: Сводка работ автора
- `get_category_analysis(category_id)`: Анализ категории

#### Методы поиска
- `search_audiobooks_comprehensive()`: Комплексный поиск с множественными фильтрами

#### Методы валидации
- `validate_audiobook_data()`: Валидация данных аудиокниги

## Схема базы данных

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

-- Индексы
CREATE INDEX idx_audiobooks_title ON audiobooks(title);
CREATE INDEX idx_audiobooks_author_id ON audiobooks(author_id);
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

## Примеры использования

См. файл `examples.py` для подробных примеров использования доменной модели.

## Зависимости

- SQLAlchemy 1.4+
- Python 3.7+

## Модуль подключения к базе данных

### connection.py
Единая точка доступа к слою персистентности для всех микросервисов:

#### Основные функции
- `get_engine()`: Получение движка базы данных (singleton)
- `get_session_factory()`: Получение фабрики сессий
- `create_session()`: Создание новой сессии
- `get_db_session()`: Контекстный менеджер для работы с сессией
- `initialize_database()`: Инициализация базы данных и создание таблиц
- `check_database_connection()`: Проверка подключения к базе данных
- `get_database_info()`: Получение информации о базе данных
- `reset_database()`: Полный сброс базы данных
- `close_connections()`: Закрытие всех соединений

#### Функции для FastAPI
- `get_db()`: Dependency injection для FastAPI

#### Конфигурация
- База данных: `audio_store.db` (SQLite)
- Автоматическое создание таблиц при инициализации
- Поддержка внешних ключей
- Логирование операций

## Установка и настройка

1. Установите зависимости:
```bash
pip install sqlalchemy
```

2. Импортируйте модули:
```python
from database.models import Base, Author, Category, Audiobook
from database.repositories import AuthorRepository, CategoryRepository, AudiobookRepository
from database.services import CatalogDomainService
from database.connection import get_db, initialize_database, get_database_info
```

3. Инициализируйте базу данных:
```python
# Автоматическое создание таблиц
initialize_database()

# Или с образцами данных
python init_db.py --sample-data
```

### Команды для работы с базой данных

#### Основные команды
```bash
# Создание таблиц
python init_db.py

# Создание таблиц с образцами данных
python init_db.py --sample-data

# Проверка состояния базы данных
python init_db.py --info --check

# Полный сброс базы данных
python init_db.py --reset

# Комбинированные операции
python init_db.py --reset --sample-data --info
```

#### Проверка и диагностика
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