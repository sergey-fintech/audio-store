#!/usr/bin/env python3
"""
Скрипт для запуска FastAPI приложения.
"""

import sys
import os
import uvicorn

# Добавляем путь к модулю database
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

def main():
    """Запуск приложения."""
    try:
        print("Starting Catalog Service...")
        uvicorn.run(
            "app:app",
            host="0.0.0.0",
            port=8001,
            reload=True,
            log_level="info"
        )
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 