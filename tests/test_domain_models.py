"""
Тесты для доменной модели каталога аудиокниг.
"""

import pytest
import sys
import os

# Добавляем путь к модулю database
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from database.models import Base, Author, Category, Audiobook
from database.repositories import AuthorRepository, CategoryRepository, AudiobookRepository
from database.services import CatalogDomainService
from database.connection import get_session_factory, initialize_database, reset_database


@pytest.fixture
def db_session():
    """Фикстура для создания тестовой сессии базы данных."""
    # Используем in-memory базу данных для тестов
    from database.connection import DATABASE_URL
    import tempfile
    
    # Создаем временный файл для тестовой базы данных
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        test_db_path = tmp_file.name
    
    # Временно изменяем URL базы данных для тестов
    import database.connection as conn
    original_url = conn.DATABASE_URL
    original_path = conn.DATABASE_PATH
    
    conn.DATABASE_URL = f"sqlite:///{test_db_path}"
    conn.DATABASE_PATH = test_db_path
    
    try:
        # Инициализируем тестовую базу данных
        initialize_database()
        session_factory = get_session_factory()
        session = session_factory()
        
        yield session
        
        session.close()
    finally:
        # Восстанавливаем оригинальные настройки
        conn.DATABASE_URL = original_url
        conn.DATABASE_PATH = original_path
        
        # Удаляем временный файл
        import os
        if os.path.exists(test_db_path):
            os.unlink(test_db_path)


@pytest.fixture
def author_repo(db_session):
    """Фикстура для репозитория авторов."""
    return AuthorRepository(db_session)


@pytest.fixture
def category_repo(db_session):
    """Фикстура для репозитория категорий."""
    return CategoryRepository(db_session)


@pytest.fixture
def audiobook_repo(db_session):
    """Фикстура для репозитория аудиокниг."""
    return AudiobookRepository(db_session)


@pytest.fixture
def catalog_service(db_session):
    """Фикстура для доменного сервиса."""
    return CatalogDomainService(db_session)


class TestAuthor:
    """Тесты для сущности Author."""
    
    def test_create_author(self, author_repo):
        """Тест создания автора."""
        author = author_repo.create("Тестовый Автор")
        assert author.id is not None
        assert author.name == "Тестовый Автор"
    
    def test_get_author_by_id(self, author_repo):
        """Тест получения автора по ID."""
        author = author_repo.create("Тестовый Автор")
        retrieved_author = author_repo.get_by_id(author.id)
        assert retrieved_author is not None
        assert retrieved_author.name == "Тестовый Автор"
    
    def test_get_author_by_name(self, author_repo):
        """Тест получения автора по имени."""
        author = author_repo.create("Тестовый Автор")
        retrieved_author = author_repo.get_by_name("Тестовый Автор")
        assert retrieved_author is not None
        assert retrieved_author.id == author.id
    
    def test_update_author(self, author_repo):
        """Тест обновления автора."""
        author = author_repo.create("Старое Имя")
        updated_author = author_repo.update(author.id, "Новое Имя")
        assert updated_author.name == "Новое Имя"
    
    def test_delete_author(self, author_repo):
        """Тест удаления автора."""
        author = author_repo.create("Тестовый Автор")
        result = author_repo.delete(author.id)
        assert result is True
        retrieved_author = author_repo.get_by_id(author.id)
        assert retrieved_author is None


class TestCategory:
    """Тесты для сущности Category."""
    
    def test_create_category(self, category_repo):
        """Тест создания категории."""
        category = category_repo.create("Фэнтези")
        assert category.id is not None
        assert category.name == "Фэнтези"
    
    def test_get_category_by_id(self, category_repo):
        """Тест получения категории по ID."""
        category = category_repo.create("Фэнтези")
        retrieved_category = category_repo.get_by_id(category.id)
        assert retrieved_category is not None
        assert retrieved_category.name == "Фэнтези"
    
    def test_get_category_by_name(self, category_repo):
        """Тест получения категории по названию."""
        category = category_repo.create("Фэнтези")
        retrieved_category = category_repo.get_by_name("Фэнтези")
        assert retrieved_category is not None
        assert retrieved_category.id == category.id
    
    def test_update_category(self, category_repo):
        """Тест обновления категории."""
        category = category_repo.create("Старая Категория")
        updated_category = category_repo.update(category.id, "Новая Категория")
        assert updated_category.name == "Новая Категория"
    
    def test_delete_category(self, category_repo):
        """Тест удаления категории."""
        category = category_repo.create("Тестовая Категория")
        result = category_repo.delete(category.id)
        assert result is True
        retrieved_category = category_repo.get_by_id(category.id)
        assert retrieved_category is None


class TestAudiobook:
    """Тесты для агрегата Audiobook."""
    
    def test_create_audiobook(self, audiobook_repo, author_repo):
        """Тест создания аудиокниги."""
        author = author_repo.create("Тестовый Автор")
        audiobook = audiobook_repo.create(
            title="Тестовая Аудиокнига",
            author_id=author.id,
            price=29.99,
            description="Описание тестовой аудиокниги"
        )
        assert audiobook.id is not None
        assert audiobook.title == "Тестовая Аудиокнига"
        assert float(audiobook.price) == 29.99
        assert audiobook.author_id == author.id
    
    def test_get_audiobook_by_id(self, audiobook_repo, author_repo):
        """Тест получения аудиокниги по ID."""
        author = author_repo.create("Тестовый Автор")
        audiobook = audiobook_repo.create(
            title="Тестовая Аудиокнига",
            author_id=author.id,
            price=29.99
        )
        retrieved_audiobook = audiobook_repo.get_by_id(audiobook.id)
        assert retrieved_audiobook is not None
        assert retrieved_audiobook.title == "Тестовая Аудиокнига"
        assert retrieved_audiobook.author is not None
        assert retrieved_audiobook.author.name == "Тестовый Автор"
    
    def test_add_category_to_audiobook(self, audiobook_repo, author_repo, category_repo):
        """Тест добавления категории к аудиокниге."""
        author = author_repo.create("Тестовый Автор")
        category = category_repo.create("Фэнтези")
        audiobook = audiobook_repo.create(
            title="Тестовая Аудиокнига",
            author_id=author.id,
            price=29.99
        )
        
        result = audiobook_repo.add_category(audiobook.id, category.id)
        assert result is True
        
        retrieved_audiobook = audiobook_repo.get_by_id(audiobook.id)
        assert len(retrieved_audiobook.categories) == 1
        assert retrieved_audiobook.categories[0].name == "Фэнтези"
    
    def test_remove_category_from_audiobook(self, audiobook_repo, author_repo, category_repo):
        """Тест удаления категории из аудиокниги."""
        author = author_repo.create("Тестовый Автор")
        category = category_repo.create("Фэнтези")
        audiobook = audiobook_repo.create(
            title="Тестовая Аудиокнига",
            author_id=author.id,
            price=29.99
        )
        
        audiobook_repo.add_category(audiobook.id, category.id)
        result = audiobook_repo.remove_category(audiobook.id, category.id)
        assert result is True
        
        retrieved_audiobook = audiobook_repo.get_by_id(audiobook.id)
        assert len(retrieved_audiobook.categories) == 0
    
    def test_search_audiobooks(self, audiobook_repo, author_repo):
        """Тест поиска аудиокниг."""
        author = author_repo.create("Тестовый Автор")
        audiobook_repo.create(
            title="Фэнтези Книга",
            author_id=author.id,
            price=29.99,
            description="Описание фэнтези книги"
        )
        audiobook_repo.create(
            title="Детектив Книга",
            author_id=author.id,
            price=24.99,
            description="Описание детектива"
        )
        
        results = audiobook_repo.search("фэнтези")
        assert len(results) == 1
        assert results[0].title == "Фэнтези Книга"
    
    def test_get_audiobooks_by_author(self, audiobook_repo, author_repo):
        """Тест получения аудиокниг по автору."""
        author1 = author_repo.create("Автор 1")
        author2 = author_repo.create("Автор 2")
        
        audiobook_repo.create("Книга 1", author1.id, 29.99)
        audiobook_repo.create("Книга 2", author1.id, 24.99)
        audiobook_repo.create("Книга 3", author2.id, 19.99)
        
        author1_books = audiobook_repo.get_by_author(author1.id)
        assert len(author1_books) == 2
        
        author2_books = audiobook_repo.get_by_author(author2.id)
        assert len(author2_books) == 1


class TestAudiobookAggregate:
    """Тесты для бизнес-логики агрегата Audiobook."""
    
    def test_add_category(self, audiobook_repo, author_repo, category_repo):
        """Тест добавления категории через агрегат."""
        author = author_repo.create("Тестовый Автор")
        category = category_repo.create("Фэнтези")
        audiobook = audiobook_repo.create(
            title="Тестовая Аудиокнига",
            author_id=author.id,
            price=29.99
        )
        
        audiobook.add_category(category)
        assert len(audiobook.categories) == 1
        assert audiobook.categories[0].name == "Фэнтези"
    
    def test_remove_category(self, audiobook_repo, author_repo, category_repo):
        """Тест удаления категории через агрегат."""
        author = author_repo.create("Тестовый Автор")
        category = category_repo.create("Фэнтези")
        audiobook = audiobook_repo.create(
            title="Тестовая Аудиокнига",
            author_id=author.id,
            price=29.99
        )
        
        audiobook.add_category(category)
        audiobook.remove_category(category)
        assert len(audiobook.categories) == 0
    
    def test_get_categories_names(self, audiobook_repo, author_repo, category_repo):
        """Тест получения названий категорий."""
        author = author_repo.create("Тестовый Автор")
        category1 = category_repo.create("Фэнтези")
        category2 = category_repo.create("Приключения")
        audiobook = audiobook_repo.create(
            title="Тестовая Аудиокнига",
            author_id=author.id,
            price=29.99
        )
        
        audiobook.add_category(category1)
        audiobook.add_category(category2)
        
        category_names = audiobook.get_categories_names()
        assert "Фэнтези" in category_names
        assert "Приключения" in category_names
        assert len(category_names) == 2
    
    def test_has_category(self, audiobook_repo, author_repo, category_repo):
        """Тест проверки принадлежности к категории."""
        author = author_repo.create("Тестовый Автор")
        category = category_repo.create("Фэнтези")
        audiobook = audiobook_repo.create(
            title="Тестовая Аудиокнига",
            author_id=author.id,
            price=29.99
        )
        
        assert audiobook.has_category("Фэнтези") is False
        audiobook.add_category(category)
        assert audiobook.has_category("Фэнтези") is True
    
    def test_update_price_validation(self, audiobook_repo, author_repo):
        """Тест валидации при обновлении цены."""
        author = author_repo.create("Тестовый Автор")
        audiobook = audiobook_repo.create(
            title="Тестовая Аудиокнига",
            author_id=author.id,
            price=29.99
        )
        
        # Тест отрицательной цены
        with pytest.raises(ValueError, match="Цена не может быть отрицательной"):
            audiobook.update_price(-10.0)
        
        # Тест корректного обновления
        audiobook.update_price(39.99)
        assert float(audiobook.price) == 39.99
    
    def test_author_name_property(self, audiobook_repo, author_repo):
        """Тест свойства author_name."""
        author = author_repo.create("Тестовый Автор")
        audiobook = audiobook_repo.create(
            title="Тестовая Аудиокнига",
            author_id=author.id,
            price=29.99
        )
        
        assert audiobook.author_name == "Тестовый Автор"
        
        # Тест с несуществующим автором
        audiobook.author = None
        assert audiobook.author_name == "Unknown Author"


class TestCatalogDomainService:
    """Тесты для доменного сервиса."""
    
    def test_create_audiobook_with_author_and_categories(self, catalog_service):
        """Тест создания аудиокниги через доменный сервис."""
        audiobook = catalog_service.create_audiobook_with_author_and_categories(
            title="Тестовая Аудиокнига",
            author_name="Новый Автор",
            price=29.99,
            category_names=["Фэнтези", "Приключения"],
            description="Описание тестовой аудиокниги"
        )
        
        assert audiobook.title == "Тестовая Аудиокнига"
        assert audiobook.author.name == "Новый Автор"
        assert len(audiobook.categories) == 2
        assert audiobook.has_category("Фэнтези")
        assert audiobook.has_category("Приключения")
    
    def test_get_catalog_statistics(self, catalog_service, author_repo, category_repo, audiobook_repo):
        """Тест получения статистики каталога."""
        # Создаем тестовые данные
        author = author_repo.create("Тестовый Автор")
        category = category_repo.create("Фэнтези")
        audiobook_repo.create("Книга 1", author.id, 29.99)
        audiobook_repo.create("Книга 2", author.id, 24.99)
        
        stats = catalog_service.get_catalog_statistics()
        
        assert stats['total_authors'] == 1
        assert stats['total_categories'] == 1
        assert stats['total_audiobooks'] == 2
        assert stats['average_price'] == 27.49
    
    def test_search_audiobooks_comprehensive(self, catalog_service, author_repo, category_repo):
        """Тест комплексного поиска аудиокниг."""
        # Создаем тестовые данные
        author = author_repo.create("Тестовый Автор")
        category = category_repo.create("Фэнтези")
        
        audiobook = catalog_service.create_audiobook_with_author_and_categories(
            title="Фэнтези Книга",
            author_name="Тестовый Автор",
            price=29.99,
            category_names=["Фэнтези"]
        )
        
        results = catalog_service.search_audiobooks_comprehensive(
            query="фэнтези",
            min_price=20.0,
            max_price=50.0
        )
        
        assert len(results) == 1
        assert results[0].title == "Фэнтези Книга"
    
    def test_validate_audiobook_data(self, catalog_service):
        """Тест валидации данных аудиокниги."""
        # Тест с некорректными данными
        validation = catalog_service.validate_audiobook_data(
            title="",
            author_id=999,
            price=-10.0,
            category_ids=[999]
        )
        
        assert validation['is_valid'] is False
        assert len(validation['errors']) > 0
        assert "Название аудиокниги не может быть пустым" in validation['errors']
        assert "Цена не может быть отрицательной" in validation['errors']
        
        # Тест с корректными данными
        author_repo = AuthorRepository(catalog_service.session)
        author = author_repo.create("Тестовый Автор")
        
        validation = catalog_service.validate_audiobook_data(
            title="Корректная Книга",
            author_id=author.id,
            price=29.99
        )
        
        assert validation['is_valid'] is True
        assert len(validation['errors']) == 0


if __name__ == "__main__":
    pytest.main([__file__]) 