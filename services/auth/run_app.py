#!/usr/bin/env python3
"""
Скрипт для запуска микросервиса аутентификации
"""

import uvicorn
import sys
import os

# Добавляем путь к корневой директории проекта для импорта моделей
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

if __name__ == "__main__":
    print("🚀 Запуск микросервиса аутентификации...")
    print("🔐 Сервис будет доступен по адресу: http://localhost:8001")
    print("📚 API документация: http://localhost:8001/docs")
    print("🔍 Health check: http://localhost:8001/health")
    print()
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )

