"""
Примеры использования доменной модели каталога аудиокниг.

Этот файл демонстрирует, как использовать созданную доменную модель
в соответствии с принципами DDD.
"""

from .models import Base, Author, Category, Audiobook
from .repositories import AuthorRepository, CategoryRepository, AudiobookRepository
from .services import CatalogDomainService
from .connection import get_session_factory, initialize_database


def setup_database():
    """
    Настройка базы данных и создание таблиц.
    """
    # Инициализация базы данных
    initialize_database()
    
    # Получение фабрики сессий
    SessionLocal = get_session_factory()
    
    return SessionLocal


def example_basic_usage():
    """
    Пример базового использования доменной модели.
    """
    print("=== Пример базового использования доменной модели ===")
    
    SessionLocal = setup_database()
    session = SessionLocal()
    
    try:
        # Создание репозиториев
        author_repo = AuthorRepository(session)
        category_repo = CategoryRepository(session)
        audiobook_repo = AudiobookRepository(session)
        
        # Создание авторов
        print("\n1. Создание авторов:")
        author1 = author_repo.create("Джордж Р.Р. Мартин")
        author2 = author_repo.create("Дж.К. Роулинг")
        print(f"Создан автор: {author1}")
        print(f"Создан автор: {author2}")
        
        # Создание категорий
        print("\n2. Создание категорий:")
        fantasy = category_repo.create("Фэнтези")
        scifi = category_repo.create("Научная фантастика")
        adventure = category_repo.create("Приключения")
        print(f"Создана категория: {fantasy}")
        print(f"Создана категория: {scifi}")
        print(f"Создана категория: {adventure}")
        
        # Создание аудиокниг
        print("\n3. Создание аудиокниг:")
        audiobook1 = audiobook_repo.create(
            title="Игра престолов",
            author_id=author1.id,
            price=29.99,
            description="Эпическая сага о борьбе за власть в Вестеросе",
            cover_image_url="https://example.com/got-cover.jpg"
        )
        
        audiobook2 = audiobook_repo.create(
            title="Гарри Поттер и философский камень",
            author_id=author2.id,
            price=24.99,
            description="Первая книга о юном волшебнике",
            cover_image_url="https://example.com/hp-cover.jpg"
        )
        
        print(f"Создана аудиокнига: {audiobook1}")
        print(f"Создана аудиокнига: {audiobook2}")
        
        # Добавление категорий к аудиокнигам
        print("\n4. Добавление категорий к аудиокнигам:")
        audiobook_repo.add_category(audiobook1.id, fantasy.id)
        audiobook_repo.add_category(audiobook1.id, adventure.id)
        audiobook_repo.add_category(audiobook2.id, fantasy.id)
        
        print(f"Категории добавлены к аудиокнигам")
        
        # Использование бизнес-методов агрегата
        print("\n5. Использование бизнес-методов агрегата:")
        audiobook = audiobook_repo.get_by_id(audiobook1.id)
        print(f"Название: {audiobook.title}")
        print(f"Автор: {audiobook.author_name}")
        print(f"Категории: {audiobook.get_categories_names()}")
        print(f"Принадлежит к фэнтези: {audiobook.has_category('Фэнтези')}")
        
        # Обновление цены
        audiobook.update_price(34.99)
        print(f"Новая цена: {audiobook.price}")
        
    finally:
        session.close()


def example_domain_service_usage():
    """
    Пример использования доменного сервиса.
    """
    print("\n=== Пример использования доменного сервиса ===")
    
    SessionLocal = setup_database()
    session = SessionLocal()
    
    try:
        # Создание доменного сервиса
        catalog_service = CatalogDomainService(session)
        
        # Создание аудиокниги с автором и категориями через доменный сервис
        print("\n1. Создание аудиокниги через доменный сервис:")
        audiobook = catalog_service.create_audiobook_with_author_and_categories(
            title="Властелин колец",
            author_name="Дж.Р.Р. Толкин",
            price=39.99,
            category_names=["Фэнтези", "Приключения"],
            description="Эпическая трилогия о кольце всевластья",
            cover_image_url="https://example.com/lotr-cover.jpg"
        )
        print(f"Создана аудиокнига: {audiobook}")
        
        # Получение статистики каталога
        print("\n2. Статистика каталога:")
        stats = catalog_service.get_catalog_statistics()
        print(f"Всего авторов: {stats['total_authors']}")
        print(f"Всего категорий: {stats['total_categories']}")
        print(f"Всего аудиокниг: {stats['total_audiobooks']}")
        print(f"Средняя цена: {stats['average_price']:.2f}")
        
        # Комплексный поиск
        print("\n3. Комплексный поиск:")
        results = catalog_service.search_audiobooks_comprehensive(
            query="фэнтези",
            min_price=20.0,
            max_price=50.0
        )
        print(f"Найдено аудиокниг: {len(results)}")
        for ab in results:
            print(f"- {ab.title} ({ab.author_name}) - {ab.price}")
        
        # Анализ автора
        print("\n4. Анализ работ автора:")
        author_repo = AuthorRepository(session)
        author = author_repo.get_by_name("Дж.Р.Р. Толкин")
        if author:
            summary = catalog_service.get_author_works_summary(author.id)
            print(f"Автор: {summary['author']['name']}")
            print(f"Всего работ: {summary['total_works']}")
            print(f"Общая стоимость: {summary['total_value']:.2f}")
            print(f"Средняя цена: {summary['average_price']:.2f}")
        
        # Валидация данных
        print("\n5. Валидация данных:")
        validation = catalog_service.validate_audiobook_data(
            title="",
            author_id=999,
            price=-10.0,
            category_ids=[999]
        )
        print(f"Валидность: {validation['is_valid']}")
        print(f"Ошибки: {validation['errors']}")
        print(f"Предупреждения: {validation['warnings']}")
        
    finally:
        session.close()


def example_aggregate_operations():
    """
    Пример операций с агрегатами.
    """
    print("\n=== Пример операций с агрегатами ===")
    
    SessionLocal = setup_database()
    session = SessionLocal()
    
    try:
        # Создание репозиториев
        author_repo = AuthorRepository(session)
        category_repo = CategoryRepository(session)
        audiobook_repo = AudiobookRepository(session)
        
        # Создание тестовых данных
        author = author_repo.create("Тестовый Автор")
        category1 = category_repo.create("Категория 1")
        category2 = category_repo.create("Категория 2")
        
        audiobook = audiobook_repo.create(
            title="Тестовая аудиокнига",
            author_id=author.id,
            price=19.99
        )
        
        print(f"Создана аудиокнига: {audiobook}")
        
        # Демонстрация работы с агрегатом
        print("\n1. Работа с категориями агрегата:")
        audiobook.add_category(category1)
        audiobook.add_category(category2)
        print(f"Категории после добавления: {audiobook.get_categories_names()}")
        
        audiobook.remove_category(category1)
        print(f"Категории после удаления: {audiobook.get_categories_names()}")
        
        print(f"Принадлежит к 'Категория 1': {audiobook.has_category('Категория 1')}")
        print(f"Принадлежит к 'Категория 2': {audiobook.has_category('Категория 2')}")
        
        # Демонстрация валидации в агрегате
        print("\n2. Валидация в агрегате:")
        try:
            audiobook.update_price(-10.0)
        except ValueError as e:
            print(f"Ошибка валидации: {e}")
        
        try:
            audiobook.update_price(25.0)
            print(f"Цена успешно обновлена: {audiobook.price}")
        except ValueError as e:
            print(f"Ошибка валидации: {e}")
        
        # Демонстрация свойств агрегата
        print("\n3. Свойства агрегата:")
        print(f"Автор: {audiobook.author_name}")
        print(f"Полное название: {audiobook}")
        
    finally:
        session.close()


if __name__ == "__main__":
    # Запуск всех примеров
    example_basic_usage()
    example_domain_service_usage()
    example_aggregate_operations()
    
    print("\n=== Все примеры выполнены успешно! ===") 