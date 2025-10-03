from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

import sys
import os

# Добавляем путь к корневой директории проекта
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from database.repositories import AudiobookRepository
from database.connection import get_db
from database.models import Audiobook

class CatalogService:
    def __init__(self, db_session: Session):
        self.audiobook_repo = AudiobookRepository(db_session)
        self.db_session = db_session

    def get_audiobook_by_id(self, audiobook_id: int) -> Optional[Audiobook]:
        """Получить аудиокнигу по ID."""
        return self.audiobook_repo.get_by_id(audiobook_id)

    def get_audiobooks_by_ids(self, audiobook_ids: List[int]) -> List[Audiobook]:
        """Получить несколько аудиокниг по списку ID."""
        return self.audiobook_repo.get_by_ids(audiobook_ids)

    def search_audiobooks(self, q: str, limit: int = 100) -> List[Audiobook]:
        """Поиск аудиокниг."""
        return self.audiobook_repo.search(q, limit=limit)

    def update_audiobook(self, audiobook_id: int, **kwargs) -> Optional[Audiobook]:
        """Обновить аудиокнигу."""
        return self.audiobook_repo.update(audiobook_id, **kwargs)

def get_catalog_service() -> CatalogService:
    """Фабрика для получения экземпляра CatalogService с сессией БД."""
    db = next(get_db())
    return CatalogService(db)
