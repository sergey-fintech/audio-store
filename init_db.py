#!/usr/bin/env python3
"""
Скрипт для инициализации базы данных Audio Store.

Этот скрипт создает базу данных MySQL и все необходимые таблицы
на основе доменных моделей.
"""

import sys
import os
import argparse
import logging

# Добавляем путь к модулю database
sys.path.append(os.path.dirname(__file__))

from database.connection import (
    initialize_database,
    get_database_info,
    check_database_connection,
    reset_database,
    get_database_path
)
from database.models import Base, Author, Category, Audiobook
from database.repositories import AuthorRepository, CategoryRepository, AudiobookRepository
from database.services import CatalogDomainService

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_sample_data():
    """
    Создает образцы данных для демонстрации функциональности.
    """
    logger.info("Создание образцов данных...")
    
    from database.connection import get_db_session
    
    with get_db_session() as session:
        # Создание репозиториев
        author_repo = AuthorRepository(session)
        category_repo = CategoryRepository(session)
        audiobook_repo = AudiobookRepository(session)
        
        # Создание авторов
        logger.info("Создание авторов...")
        authors = [
            author_repo.create("Джордж Р.Р. Мартин"),
            author_repo.create("Дж.К. Роулинг"),
            author_repo.create("Дж.Р.Р. Толкин"),
            author_repo.create("Фрэнк Герберт"),
            author_repo.create("Айзек Азимов")
        ]
        
        # Создание категорий
        logger.info("Создание категорий...")
        categories = [
            category_repo.create("Фэнтези"),
            category_repo.create("Научная фантастика"),
            category_repo.create("Приключения"),
            category_repo.create("Детектив"),
            category_repo.create("Роман")
        ]
        
        # Создание аудиокниг
        logger.info("Создание аудиокниг...")
        audiobooks = [
            {
                "title": "Игра престолов",
                "author_name": "Джордж Р.Р. Мартин",
                "price": 29.99,
                "description": "Эпическая сага о борьбе за власть в Вестеросе",
                "category_names": ["Фэнтези", "Приключения"]
            },
            {
                "title": "Гарри Поттер и философский камень",
                "author_name": "Дж.К. Роулинг",
                "price": 24.99,
                "description": "Первая книга о юном волшебнике",
                "category_names": ["Фэнтези", "Приключения"]
            },
            {
                "title": "Властелин колец",
                "author_name": "Дж.Р.Р. Толкин",
                "price": 39.99,
                "description": "Эпическая трилогия о кольце всевластья",
                "category_names": ["Фэнтези", "Приключения"]
            },
            {
                "title": "Дюна",
                "author_name": "Фрэнк Герберт",
                "price": 34.99,
                "description": "Классический роман научной фантастики",
                "category_names": ["Научная фантастика", "Приключения"]
            },
            {
                "title": "Основание",
                "author_name": "Айзек Азимов",
                "price": 27.99,
                "description": "Цикл романов о галактической империи",
                "category_names": ["Научная фантастика"]
            }
        ]
        
        # Создание аудиокниг через доменный сервис
        catalog_service = CatalogDomainService(session)
        for audiobook_data in audiobooks:
            catalog_service.create_audiobook_with_author_and_categories(**audiobook_data)
        
        logger.info(f"Создано {len(authors)} авторов, {len(categories)} категорий, {len(audiobooks)} аудиокниг")


def main():
    """
    Основная функция скрипта.
    """
    parser = argparse.ArgumentParser(
        description="Инициализация базы данных Audio Store"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Сбросить базу данных (удалить все данные)"
    )
    parser.add_argument(
        "--sample-data",
        action="store_true",
        help="Создать образцы данных"
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Показать информацию о базе данных"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Проверить подключение к базе данных"
    )
    
    args = parser.parse_args()
    
    try:
        # Проверка подключения
        if args.check:
            logger.info("Проверка подключения к базе данных...")
            if check_database_connection():
                logger.info("✅ Подключение к базе данных успешно")
            else:
                logger.error("❌ Ошибка подключения к базе данных")
                return 1
        
        # Сброс базы данных
        if args.reset:
            logger.warning("Сброс базы данных - все данные будут удалены!")
            reset_database()
            logger.info("✅ База данных сброшена")
        
        # Инициализация базы данных
        logger.info("Инициализация базы данных...")
        initialize_database()
        logger.info("✅ База данных инициализирована")
        
        # Создание образцов данных
        if args.sample_data:
            create_sample_data()
            logger.info("✅ Образцы данных созданы")
        
        # Показ информации о базе данных
        if args.info:
            logger.info("Информация о базе данных:")
            info = get_database_info()
            print(f"  Путь к базе данных: {info['database_path']}")
            print(f"  URL: {info['database_url']}")
            print(f"  Статус подключения: {'✅' if info['connection_status'] else '❌'}")
            print(f"  Таблицы: {', '.join(info['tables'])}")
        
        # Показ информации о базе данных
        logger.info(f"✅ База данных MySQL готова к использованию")
        
        logger.info("🎉 Инициализация базы данных завершена успешно!")
        return 0
        
    except Exception as e:
        logger.error(f"❌ Ошибка при инициализации базы данных: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
