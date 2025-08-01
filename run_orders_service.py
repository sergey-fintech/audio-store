#!/usr/bin/env python3
"""
Финальный скрипт для запуска микросервиса 'Заказы' из корневой директории
"""

import sys
import os
import uvicorn

# Убеждаемся, что мы в корневой директории проекта
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def main():
    print("🚀 Запуск микросервиса 'Заказы'...")
    print("📍 Адрес: http://localhost:8003")
    print("📚 API документация: http://localhost:8003/docs")
    print("🔍 Health check: http://localhost:8003/health")
    print()
    
    try:
        # Тестируем импорт
        print("🔧 Проверка импортов...")
        from services.orders.main import app
        print("✅ Импорт приложения успешен")
        
        # Запускаем сервер
        print("🚀 Запуск сервера...")
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8003,
            reload=False,
            log_level="info"
        )
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("📋 Убедитесь, что все зависимости установлены")
        return 1
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 