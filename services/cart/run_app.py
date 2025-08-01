#!/usr/bin/env python3
"""
Скрипт для запуска микросервиса "Корзина"
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    ) 