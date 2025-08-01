#!/usr/bin/env python3
"""
Тестовый файл для проверки импортов.
"""

import sys
import os

# Добавляем путь к модулю database
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

print("Testing imports...")

try:
    from database.connection import get_db, initialize_database, get_database_info
    print("✓ database.connection imported successfully")
except Exception as e:
    print(f"✗ Error importing database.connection: {e}")

try:
    from schemas import AudiobookSchema
    print("✓ schemas imported successfully")
except Exception as e:
    print(f"✗ Error importing schemas: {e}")

try:
    from services import CatalogApplicationService
    print("✓ services imported successfully")
except Exception as e:
    print(f"✗ Error importing services: {e}")

print("Import test completed.") 