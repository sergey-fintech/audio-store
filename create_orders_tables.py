#!/usr/bin/env python3
"""
Скрипт для создания таблиц заказов в базе данных
"""

import sys
import os

# Добавляем корневую директорию проекта в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.connection import get_engine
from database.models import Base, Order, OrderItem

def create_orders_tables():
    """Создает таблицы для заказов в базе данных"""
    try:
        print("🔧 Создание таблиц для заказов...")
        
        engine = get_engine()
        
        # Создаем таблицы Order и OrderItem
        Order.__table__.create(engine, checkfirst=True)
        OrderItem.__table__.create(engine, checkfirst=True)
        
        print("✅ Таблицы заказов успешно созданы!")
        print("📋 Созданные таблицы:")
        print("   - orders (заказы)")
        print("   - order_items (позиции заказов)")
        
    except Exception as e:
        print(f"❌ Ошибка при создании таблиц: {str(e)}")
        sys.exit(1)

def check_tables_exist():
    """Проверяет существование таблиц заказов"""
    try:
        from sqlalchemy import inspect
        
        engine = get_engine()
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        required_tables = ['orders', 'order_items']
        missing_tables = [table for table in required_tables if table not in tables]
        
        if missing_tables:
            print(f"⚠️  Отсутствуют таблицы: {missing_tables}")
            return False
        else:
            print("✅ Все таблицы заказов существуют")
            return True
            
    except Exception as e:
        print(f"❌ Ошибка при проверке таблиц: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Скрипт создания таблиц заказов")
    print("=" * 50)
    
    # Проверяем существование таблиц
    if check_tables_exist():
        print("📝 Таблицы уже существуют, повторное создание не требуется")
    else:
        # Создаем таблицы
        create_orders_tables()
        
        # Проверяем результат
        if check_tables_exist():
            print("🎉 Все таблицы заказов успешно созданы!")
        else:
            print("❌ Не удалось создать все таблицы")
            sys.exit(1)
    
    print("=" * 50)
    print("✅ Скрипт завершен успешно") 