#!/usr/bin/env python3
"""
Скрипт для запуска AI Recommender Service
"""

import uvicorn
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

if __name__ == "__main__":
    # Проверяем наличие API ключа
    if not os.getenv("OPENROUTER_API_KEY"):
        print("⚠️  ВНИМАНИЕ: OPENROUTER_API_KEY не установлен!")
        print("Установите переменную окружения OPENROUTER_API_KEY для работы с LLM")
        print("Пример: set OPENROUTER_API_KEY=your_api_key_here")
    
    print("🚀 Запуск микросервиса рекомендаций...")
    print("🤖 Сервис будет доступен по адресу: http://localhost:8005")
    print("📚 API документация: http://localhost:8005/docs")
    print("🔍 Health check: http://localhost:8005/health")
    print()
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8005,
        reload=True,
        log_level="info"
    )
