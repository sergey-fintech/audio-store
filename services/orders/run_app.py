#!/usr/bin/env python3
"""
Скрипт для запуска микросервиса 'Заказы'
"""

import uvicorn
import sys
import os

# Добавляем корневую директорию проекта в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

if __name__ == "__main__":
    print("🚀 Запуск микросервиса 'Заказы'...")
    print("📍 Адрес: http://localhost:8003")
    print("📚 API документация: http://localhost:8003/docs")
    print("🔍 Health check: http://localhost:8003/health")
    print()
    
    uvicorn.run(
        "services.orders.main:app",
        host="0.0.0.0",
        port=8003,
        reload=False,  # Отключаем reload для стабильности
        log_level="info"
    ) 