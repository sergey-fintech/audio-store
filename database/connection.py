"""
Модуль для подключения к базе данных MySQL.

Этот модуль служит единой точкой доступа к слою персистентности
для всех микросервисов системы Audio Store.
"""

import os
from typing import Optional
from sqlalchemy import create_engine, event, inspect
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
import logging
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загружаем переменные окружения из .env файла в корне проекта
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(_project_root, '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    logger.info(".env файл загружен")

# Конфигурация базы данных
# Сначала пытаемся получить из переменных окружения, потом используем значение по умолчанию для локальной разработки
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://app_user:strong_password_123@127.0.0.1:3306/audio_store")

# Глобальные переменные для движка и фабрики сессий
_engine: Optional[create_engine] = None
_session_factory: Optional[sessionmaker] = None

# Создаем SessionLocal на уровне модуля
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_database_url() -> str:
    """
    Возвращает URL для подключения к базе данных.
    
    Returns:
        URL для подключения к MySQL базе данных
    """
    return DATABASE_URL


def get_database_path() -> str:
    """
    Возвращает путь к файлу базы данных.
    
    Returns:
        Путь к файлу базы данных (для совместимости)
    """
    return "mysql://127.0.0.1:3306/audio_store"


def create_database_engine(
    echo: bool = False,
    **kwargs
) -> create_engine:
    """
    Создает движок базы данных с настраиваемыми параметрами.
    
    Args:
        echo: Включить логирование SQL запросов
        poolclass: Класс пула соединений
        **kwargs: Дополнительные параметры для create_engine
        
    Returns:
        Настроенный движок SQLAlchemy
    """
    # Параметры по умолчанию для MySQL
    default_kwargs = {
        "pool_pre_ping": True,
        "pool_recycle": 3600,  # Пересоздавать соединения каждый час
        "pool_size": 10,       # Размер пула соединений
        "max_overflow": 20,    # Максимальное количество дополнительных соединений
    }
    
    default_kwargs.update(kwargs)
    
    engine = create_engine(
        DATABASE_URL,
        echo=echo,
        **default_kwargs
    )
    
    return engine


def get_engine() -> create_engine:
    """
    Возвращает глобальный движок базы данных.
    Создает новый движок, если он еще не создан.
    
    Returns:
        Движок SQLAlchemy
    """
    global _engine
    
    if _engine is None:
        logger.info("Создание движка базы данных...")
        _engine = create_database_engine()
        logger.info(f"Движок базы данных создан: {DATABASE_URL}")
    
    return _engine


def get_session_factory() -> sessionmaker:
    """
    Возвращает фабрику сессий базы данных.
    Создает новую фабрику, если она еще не создана.
    
    Returns:
        Фабрика сессий SQLAlchemy
    """
    global _session_factory
    
    if _session_factory is None:
        logger.info("Создание фабрики сессий...")
        engine = get_engine()
        _session_factory = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine
        )
        logger.info("Фабрика сессий создана")
    
    return _session_factory


def create_session() -> Session:
    """
    Создает новую сессию базы данных.
    
    Returns:
        Новая сессия SQLAlchemy
    """
    session_factory = get_session_factory()
    return session_factory()


@contextmanager
def get_db_session():
    """
    Контекстный менеджер для работы с сессией базы данных.
    Автоматически закрывает сессию после использования.
    
    Yields:
        Сессия базы данных
    """
    session = create_session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Ошибка в сессии базы данных: {e}")
        raise
    finally:
        session.close()


def initialize_database(create_tables: bool = True, drop_tables: bool = False) -> None:
    """
    Инициализирует базу данных - создает все таблицы на основе доменных моделей.
    
    Args:
        create_tables: Создавать ли таблицы
        drop_tables: Удалять ли существующие таблицы перед созданием
    """
    from .models import Base
    
    engine = get_engine()
    
    try:
        if drop_tables:
            logger.info("Удаление существующих таблиц...")
            Base.metadata.drop_all(engine)
            logger.info("Таблицы удалены")
        
        if create_tables:
            logger.info("Создание таблиц базы данных...")
            Base.metadata.create_all(engine)
            logger.info("Таблицы созданы успешно")
            
            # Проверяем созданные таблицы
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            logger.info(f"Созданные таблицы: {', '.join(tables)}")
    
    except Exception as e:
        logger.error(f"Ошибка при инициализации базы данных: {e}")
        raise


def check_database_connection() -> bool:
    """
    Проверяет подключение к базе данных.
    
    Returns:
        True, если подключение успешно, False в противном случае
    """
    try:
        engine = get_engine()
        with engine.connect() as connection:
            result = connection.execute("SELECT 1")
            result.fetchone()
        logger.info("Подключение к базе данных успешно")
        return True
    except Exception as e:
        logger.error(f"Ошибка подключения к базе данных: {e}")
        return False


def get_database_info() -> dict:
    """
    Возвращает информацию о базе данных.
    
    Returns:
        Словарь с информацией о базе данных
    """
    engine = get_engine()
    inspector = inspect(engine)
    
    info = {
        "database_url": DATABASE_URL,
        "database_path": get_database_path(),
        "tables": inspector.get_table_names(),
        "connection_status": check_database_connection()
    }
    
    return info


def reset_database() -> None:
    """
    Полностью сбрасывает базу данных - удаляет все таблицы и создает заново.
    ВНИМАНИЕ: Это удалит все данные!
    """
    logger.warning("Сброс базы данных - все данные будут удалены!")
    
    try:
        initialize_database(create_tables=True, drop_tables=True)
        logger.info("База данных успешно сброшена")
    except Exception as e:
        logger.error(f"Ошибка при сбросе базы данных: {e}")
        raise


def close_connections() -> None:
    """
    Закрывает все соединения с базой данных.
    """
    global _engine, _session_factory
    
    if _engine:
        logger.info("Закрытие соединений с базой данных...")
        _engine.dispose()
        _engine = None
        _session_factory = None
        logger.info("Соединения с базой данных закрыты")


# Функция для FastAPI dependency injection
def get_db():
    """
    Функция для использования в FastAPI как dependency.
    
    Yields:
        Сессия базы данных
    """
    with get_db_session() as session:
        yield session


# Инициализация при импорте модуля
def _initialize():
    """
    Инициализация модуля при импорте.
    """
    logger.info("Инициализация модуля подключения к базе данных")
    logger.info(f"Подключение к MySQL: {DATABASE_URL}")


# Запускаем инициализацию при импорте модуля
_initialize()
