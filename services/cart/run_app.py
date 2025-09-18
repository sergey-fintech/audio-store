#!/usr/bin/env python3
"""
Скрипт для запуска микросервиса "Корзина"
"""

import uvicorn

if __name__ == "__main__":
    print("🚀 Запуск микросервиса корзины...")
    print("🛒 Сервис будет доступен по адресу: http://localhost:8004")
    print("📚 API документация: http://localhost:8004/docs")
    print("🔍 Health check: http://localhost:8004/health")
    print()
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8004,
        reload=True,
        log_level="info"
    ) 