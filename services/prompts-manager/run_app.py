"""
Скрипт для запуска сервиса управления промптами.

Использование:
    python run_app.py
"""

import uvicorn
import sys
import os

# Добавляем путь к корню проекта
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

if __name__ == "__main__":
    print("🚀 Запуск Prompts Manager Service...")
    print("📍 Порт: 8006")
    print("🌐 URL: http://localhost:8006")
    print("📚 Документация API: http://localhost:8006/docs")
    print("🔧 ReDoc: http://localhost:8006/redoc")
    print("-" * 50)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8006,
        reload=True,
        log_level="info"
    )
