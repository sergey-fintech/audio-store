#!/usr/bin/env python3
"""
Скрипт для запуска микросервиса каталога
"""

import sys
import os
import uvicorn

# Добавляем путь к модулю database
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

def main():
    """Запуск приложения."""
    try:
        print("🚀 Запуск микросервиса каталога...")
        print("📚 Сервис будет доступен по адресу: http://localhost:8002")
        print("📖 API документация: http://localhost:8002/docs")
        print("🔍 Health check: http://localhost:8002/health")
        print()
        
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8002,
            reload=True,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Ошибка запуска приложения: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 