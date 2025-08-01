"""
Тесты для модуля подключения к базе данных.
"""

import pytest
import os
import tempfile
import sys

# Добавляем путь к модулю database
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from database.connection import (
    get_database_url,
    get_database_path,
    create_database_engine,
    get_engine,
    get_session_factory,
    create_session,
    get_db_session,
    initialize_database,
    check_database_connection,
    get_database_info,
    reset_database,
    close_connections,
    get_db
)
from sqlalchemy import inspect
from database.models import Base


class TestDatabaseConnection:
    """Тесты для модуля подключения к базе данных."""
    
    def test_get_database_url(self):
        """Тест получения URL базы данных."""
        url = get_database_url()
        assert url == "sqlite:///audio_store.db"
    
    def test_get_database_path(self):
        """Тест получения пути к файлу базы данных."""
        path = get_database_path()
        assert path == "audio_store.db"
    
    def test_create_database_engine(self):
        """Тест создания движка базы данных."""
        engine = create_database_engine(echo=False)
        assert engine is not None
        assert str(engine.url) == "sqlite:///audio_store.db"
    
    def test_get_engine_singleton(self):
        """Тест, что get_engine возвращает один и тот же движок."""
        # Сбрасываем глобальные переменные
        import database.connection as conn
        conn._engine = None
        
        engine1 = get_engine()
        engine2 = get_engine()
        assert engine1 is engine2
    
    def test_get_session_factory(self):
        """Тест получения фабрики сессий."""
        # Сбрасываем глобальные переменные
        import database.connection as conn
        conn._session_factory = None
        
        session_factory = get_session_factory()
        assert session_factory is not None
        
        # Проверяем, что фабрика создает сессии
        session = session_factory()
        assert session is not None
        session.close()
    
    def test_create_session(self):
        """Тест создания сессии."""
        session = create_session()
        assert session is not None
        session.close()
    
    def test_get_db_session_context_manager(self):
        """Тест контекстного менеджера для сессии."""
        with get_db_session() as session:
            assert session is not None
            # Проверяем, что сессия активна
            result = session.execute("SELECT 1")
            assert result.fetchone()[0] == 1
    
    def test_get_db_session_rollback_on_error(self):
        """Тест отката транзакции при ошибке."""
        with pytest.raises(Exception):
            with get_db_session() as session:
                # Выполняем некорректный SQL для вызова ошибки
                session.execute("SELECT * FROM non_existent_table")
    
    def test_initialize_database(self):
        """Тест инициализации базы данных."""
        # Используем временную базу данных для теста
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            test_db_path = tmp_file.name
        
        try:
            # Временно изменяем настройки базы данных
            import database.connection as conn
            original_url = conn.DATABASE_URL
            original_path = conn.DATABASE_PATH
            
            conn.DATABASE_URL = f"sqlite:///{test_db_path}"
            conn.DATABASE_PATH = test_db_path
            
            # Сбрасываем глобальные переменные
            conn._engine = None
            conn._session_factory = None
            
            # Инициализируем базу данных
            initialize_database()
            
            # Проверяем, что файл базы данных создан
            assert os.path.exists(test_db_path)
            
            # Проверяем, что таблицы созданы
            engine = get_engine()
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            expected_tables = ['authors', 'categories', 'audiobooks', 'audiobook_category']
            
            for table in expected_tables:
                assert table in tables
            
        finally:
            # Закрываем соединения
            close_connections()
            
            # Восстанавливаем оригинальные настройки
            conn.DATABASE_URL = original_url
            conn.DATABASE_PATH = original_path
            conn._engine = None
            conn._session_factory = None
            
            # Удаляем временный файл
            if os.path.exists(test_db_path):
                try:
                    os.unlink(test_db_path)
                except PermissionError:
                    # Файл может быть занят, игнорируем ошибку
                    pass
    
    def test_initialize_database_with_drop_tables(self):
        """Тест инициализации базы данных с удалением таблиц."""
        # Используем временную базу данных для теста
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            test_db_path = tmp_file.name
        
        try:
            # Временно изменяем настройки базы данных
            import database.connection as conn
            original_url = conn.DATABASE_URL
            original_path = conn.DATABASE_PATH
            
            conn.DATABASE_URL = f"sqlite:///{test_db_path}"
            conn.DATABASE_PATH = test_db_path
            
            # Сбрасываем глобальные переменные
            conn._engine = None
            conn._session_factory = None
            
            # Создаем таблицы
            initialize_database(create_tables=True, drop_tables=False)
            
            # Удаляем и пересоздаем таблицы
            initialize_database(create_tables=True, drop_tables=True)
            
            # Проверяем, что таблицы все еще существуют
            engine = get_engine()
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            expected_tables = ['authors', 'categories', 'audiobooks', 'audiobook_category']
            
            for table in expected_tables:
                assert table in tables
            
        finally:
            # Закрываем соединения
            close_connections()
            
            # Восстанавливаем оригинальные настройки
            conn.DATABASE_URL = original_url
            conn.DATABASE_PATH = original_path
            conn._engine = None
            conn._session_factory = None
            
            # Удаляем временный файл
            if os.path.exists(test_db_path):
                try:
                    os.unlink(test_db_path)
                except PermissionError:
                    # Файл может быть занят, игнорируем ошибку
                    pass
    
    def test_check_database_connection(self):
        """Тест проверки подключения к базе данных."""
        # Используем временную базу данных для теста
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            test_db_path = tmp_file.name
        
        try:
            # Временно изменяем настройки базы данных
            import database.connection as conn
            original_url = conn.DATABASE_URL
            original_path = conn.DATABASE_PATH
            
            conn.DATABASE_URL = f"sqlite:///{test_db_path}"
            conn.DATABASE_PATH = test_db_path
            
            # Сбрасываем глобальные переменные
            conn._engine = None
            conn._session_factory = None
            
            # Инициализируем базу данных
            initialize_database()
            
            # Проверяем подключение
            assert check_database_connection() is True
            
        finally:
            # Закрываем соединения
            close_connections()
            
            # Восстанавливаем оригинальные настройки
            conn.DATABASE_URL = original_url
            conn.DATABASE_PATH = original_path
            conn._engine = None
            conn._session_factory = None
            
            # Удаляем временный файл
            if os.path.exists(test_db_path):
                try:
                    os.unlink(test_db_path)
                except PermissionError:
                    # Файл может быть занят, игнорируем ошибку
                    pass
    
    def test_get_database_info(self):
        """Тест получения информации о базе данных."""
        # Используем временную базу данных для теста
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            test_db_path = tmp_file.name
        
        try:
            # Временно изменяем настройки базы данных
            import database.connection as conn
            original_url = conn.DATABASE_URL
            original_path = conn.DATABASE_PATH
            
            conn.DATABASE_URL = f"sqlite:///{test_db_path}"
            conn.DATABASE_PATH = test_db_path
            
            # Сбрасываем глобальные переменные
            conn._engine = None
            conn._session_factory = None
            
            # Инициализируем базу данных
            initialize_database()
            
            # Получаем информацию о базе данных
            info = get_database_info()
            
            # Проверяем структуру информации
            assert 'database_url' in info
            assert 'database_path' in info
            assert 'tables' in info
            assert 'connection_status' in info
            assert 'file_size' in info
            assert 'file_exists' in info
            
            # Проверяем значения
            assert info['database_url'] == f"sqlite:///{test_db_path}"
            assert info['database_path'] == test_db_path
            assert info['file_exists'] is True
            assert info['file_size'] > 0
            assert info['connection_status'] is True
            
            # Проверяем, что все таблицы присутствуют
            expected_tables = ['authors', 'categories', 'audiobooks', 'audiobook_category']
            for table in expected_tables:
                assert table in info['tables']
            
        finally:
            # Закрываем соединения
            close_connections()
            
            # Восстанавливаем оригинальные настройки
            conn.DATABASE_URL = original_url
            conn.DATABASE_PATH = original_path
            conn._engine = None
            conn._session_factory = None
            
            # Удаляем временный файл
            if os.path.exists(test_db_path):
                try:
                    os.unlink(test_db_path)
                except PermissionError:
                    # Файл может быть занят, игнорируем ошибку
                    pass
    
    def test_reset_database(self):
        """Тест сброса базы данных."""
        # Используем временную базу данных для теста
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            test_db_path = tmp_file.name
        
        try:
            # Временно изменяем настройки базы данных
            import database.connection as conn
            original_url = conn.DATABASE_URL
            original_path = conn.DATABASE_PATH
            
            conn.DATABASE_URL = f"sqlite:///{test_db_path}"
            conn.DATABASE_PATH = test_db_path
            
            # Сбрасываем глобальные переменные
            conn._engine = None
            conn._session_factory = None
            
            # Инициализируем базу данных
            initialize_database()
            
            # Добавляем тестовые данные
            with get_db_session() as session:
                from database.models import Author
                author = Author(name="Test Author")
                session.add(author)
                session.commit()
            
            # Сбрасываем базу данных
            reset_database()
            
            # Проверяем, что таблицы все еще существуют
            engine = get_engine()
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            expected_tables = ['authors', 'categories', 'audiobooks', 'audiobook_category']
            
            for table in expected_tables:
                assert table in tables
            
            # Проверяем, что данные удалены
            with get_db_session() as session:
                from database.models import Author
                authors = session.query(Author).all()
                assert len(authors) == 0
            
        finally:
            # Закрываем соединения
            close_connections()
            
            # Восстанавливаем оригинальные настройки
            conn.DATABASE_URL = original_url
            conn.DATABASE_PATH = original_path
            conn._engine = None
            conn._session_factory = None
            
            # Удаляем временный файл
            if os.path.exists(test_db_path):
                try:
                    os.unlink(test_db_path)
                except PermissionError:
                    # Файл может быть занят, игнорируем ошибку
                    pass
    
    def test_close_connections(self):
        """Тест закрытия соединений с базой данных."""
        # Получаем движок и фабрику сессий
        engine = get_engine()
        session_factory = get_session_factory()
        
        # Закрываем соединения
        close_connections()
        
        # Проверяем, что глобальные переменные сброшены
        import database.connection as conn
        assert conn._engine is None
        assert conn._session_factory is None
    
    def test_get_db_dependency(self):
        """Тест функции get_db для FastAPI dependency injection."""
        # Проверяем, что функция get_db является генератором
        db_gen = get_db()
        assert hasattr(db_gen, '__iter__')
        
        # Проверяем, что функция возвращает сессию
        session = next(db_gen)
        assert session is not None
        session.close()


if __name__ == "__main__":
    pytest.main([__file__]) 