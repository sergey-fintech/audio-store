#!/usr/bin/env python3
"""
Скрипт для настройки базы данных.
Удаляет дублирующие файлы БД и инициализирует основную БД с тестовыми данными.
"""

import os
import sys
import shutil

def remove_duplicate_database():
    """Удаляет дублирующую базу данных из services/catalog/."""
    duplicate_path = "services/catalog/audio_store.db"
    if os.path.exists(duplicate_path):
        try:
            os.remove(duplicate_path)
            print(f"✓ Удален дублирующий файл: {duplicate_path}")
        except Exception as e:
            print(f"✗ Ошибка при удалении {duplicate_path}: {e}")
    else:
        print(f"✓ Дублирующий файл не найден: {duplicate_path}")

def initialize_database():
    """Инициализирует базу данных с тестовыми данными."""
    try:
        # Импортируем модули для работы с БД
        sys.path.append(os.path.dirname(__file__))
        from database.connection import initialize_database
        from database.services import CatalogDomainService
        from database.connection import create_session
        
        print("Инициализация базы данных...")
        initialize_database()
        
        # Создаем тестовые данные
        print("Создание тестовых данных...")
        with create_session() as session:
            domain_service = CatalogDomainService(session)
            
            # Создаем авторов
            print("Создание авторов...")
            author1 = domain_service.create_audiobook_with_author_and_categories(
                title="1984",
                author_name="Джордж Оруэлл",
                price=29.99,
                description="Классический роман-антиутопия о тоталитарном обществе",
                category_names=["Фантастика", "Классика", "Антиутопия"],
                cover_image_url="https://example.com/1984.jpg"
            )
            
            author2 = domain_service.create_audiobook_with_author_and_categories(
                title="Мастер и Маргарита",
                author_name="Михаил Булгаков",
                price=34.99,
                description="Великий роман о добре и зле, любви и предательстве",
                category_names=["Классика", "Мистика", "Роман"],
                cover_image_url="https://example.com/master-margarita.jpg"
            )
            
            author3 = domain_service.create_audiobook_with_author_and_categories(
                title="Война и мир",
                author_name="Лев Толстой",
                price=39.99,
                description="Эпический роман о русском обществе во время наполеоновских войн",
                category_names=["Классика", "Исторический роман", "Эпос"],
                cover_image_url="https://example.com/war-peace.jpg"
            )
            
            author4 = domain_service.create_audiobook_with_author_and_categories(
                title="Преступление и наказание",
                author_name="Федор Достоевский",
                price=32.99,
                description="Психологический роман о преступлении и его последствиях",
                category_names=["Классика", "Психологический роман", "Философия"],
                cover_image_url="https://example.com/crime-punishment.jpg"
            )
            
            author5 = domain_service.create_audiobook_with_author_and_categories(
                title="Гарри Поттер и философский камень",
                author_name="Джоан Роулинг",
                price=24.99,
                description="Первая книга о юном волшебнике Гарри Поттере",
                category_names=["Фэнтези", "Детская литература", "Приключения"],
                cover_image_url="https://example.com/harry-potter.jpg"
            )
            
            author6 = domain_service.create_audiobook_with_author_and_categories(
                title="Властелин колец: Братство кольца",
                author_name="Джон Рональд Руэл Толкин",
                price=44.99,
                description="Эпическая фэнтези-сага о путешествии хоббита Фродо",
                category_names=["Фэнтези", "Эпос", "Приключения"],
                cover_image_url="https://example.com/lotr.jpg"
            )
            
            author7 = domain_service.create_audiobook_with_author_and_categories(
                title="Дюна",
                author_name="Фрэнк Герберт",
                price=49.99,
                description="Научно-фантастический роман о планете Арракис",
                category_names=["Научная фантастика", "Эпос", "Философия"],
                cover_image_url="https://example.com/dune.jpg"
            )
            
            author8 = domain_service.create_audiobook_with_author_and_categories(
                title="Сто лет одиночества",
                author_name="Габриэль Гарсиа Маркес",
                price=36.99,
                description="Магический реализм о семье Буэндиа",
                category_names=["Магический реализм", "Классика", "Роман"],
                cover_image_url="https://example.com/hundred-years.jpg"
            )
            
            print("✓ Тестовые данные созданы успешно!")
            
            # Показываем статистику
            stats = domain_service.get_catalog_statistics()
            print(f"\nСтатистика каталога:")
            print(f"- Авторов: {stats['total_authors']}")
            print(f"- Категорий: {stats['total_categories']}")
            print(f"- Аудиокниг: {stats['total_audiobooks']}")
            print(f"- Средняя цена: {stats['average_price']:.2f}")
            
    except Exception as e:
        print(f"✗ Ошибка при инициализации базы данных: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Основная функция."""
    print("=== Настройка базы данных Audio Store ===\n")
    
    # Удаляем дублирующую базу данных
    remove_duplicate_database()
    
    # Инициализируем основную базу данных
    initialize_database()
    
    print("\n=== Настройка завершена ===")
    print("База данных готова к использованию!")
    print("Файл базы данных: audio_store.db")

if __name__ == "__main__":
    main() 