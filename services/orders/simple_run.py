#!/usr/bin/env python3
"""
Упрощенный скрипт для запуска микросервиса 'Заказы'
"""

import sys
import os

# Добавляем корневую директорию проекта в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

print("🚀 Запуск микросервиса 'Заказы' (упрощенная версия)...")
print("📍 Адрес: http://localhost:8003")

try:
    # Импортируем приложение
    from services.orders.main import app
    print("✅ Приложение импортировано успешно")
    
    # Запускаем uvicorn без reload
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8003,
        reload=False,  # Отключаем reload
        log_level="info"
    )
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("📋 Проверьте, что вы запускаете скрипт из корневой директории проекта")
except Exception as e:
    print(f"❌ Ошибка запуска: {e}")
    
if __name__ == "__main__":
    pass 