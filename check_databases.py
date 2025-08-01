#!/usr/bin/env python3
"""
Скрипт для проверки состояния баз данных
"""

import sqlite3
import os

def check_database(db_path, name):
    """Проверяет состояние базы данных"""
    if not os.path.exists(db_path):
        print(f"❌ {name}: файл не существует ({db_path})")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Проверяем таблицы
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"📊 {name} ({db_path}):")
        print(f"   Таблицы: {tables}")
        
        # Проверяем количество записей в основных таблицах
        for table in ['authors', 'categories', 'audiobooks']:
            if table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"   {table}: {count} записей")
                
                # Показываем первые записи
                if count > 0:
                    cursor.execute(f"SELECT * FROM {table} LIMIT 3")
                    rows = cursor.fetchall()
                    print(f"     Примеры: {rows}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Ошибка при проверке {name}: {e}")

def main():
    """Основная функция"""
    print("🔍 Проверка состояния баз данных")
    print("=" * 50)
    
    # Проверяем корневую базу данных
    check_database("audio_store.db", "Корневая БД")
    
    print()
    
    # Проверяем базу данных каталога
    check_database("services/catalog/audio_store.db", "БД Каталога")
    
    print("\n💡 Если в каталоге нет данных, нужно:")
    print("   1. Удалить services/catalog/audio_store.db")
    print("   2. Настроить каталог на использование корневой БД")
    print("   3. Или скопировать данные из корневой БД в каталог")

if __name__ == "__main__":
    main() 