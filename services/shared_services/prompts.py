from sqlalchemy.orm import Session
from typing import Optional

import sys
import os

# Добавляем путь к корневой директории проекта
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from database.models import Prompt
from database.connection import get_db

class PromptsService:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get_prompt_by_name(self, prompt_name: str) -> Optional[Prompt]:
        """Получить промпт по имени."""
        return self.db_session.query(Prompt).filter(Prompt.name == prompt_name).first()

def get_prompts_service() -> PromptsService:
    """Фабрика для получения экземпляра PromptsService с сессией БД."""
    db = next(get_db())
    return PromptsService(db)

