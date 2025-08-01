#!/usr/bin/env python3
"""
Скрипт для добавления тестовых данных в базу данных
"""

import sys
import os
from decimal import Decimal

# Добавляем корневую директорию проекта в путь
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def add_test_data():
    """Добавляет тестовые данные в базу"""
    try:
        from database.connection import get_db_session
        from database.models import Author, Category, Audiobook
        
        print("🔧 Добавление тестовых данных...")
        
        with get_db_session() as db:
            # Проверяем, есть ли уже данные
            existing_count = db.query(Audiobook).count()
            print(f"📊 Текущее количество аудиокниг в базе: {existing_count}")
            
            if existing_count > 0:
                print(f"✅ В базе уже есть {existing_count} аудиокниг")
                
                # Покажем существующие книги
                books = db.query(Audiobook).all()
                print("\n📚 Существующие аудиокниги:")
                for book in books:
                    print(f"   {book.id}. {book.title} - {book.price} руб.")
                return True
            
            # Создаем авторов
            print("👤 Создание авторов...")
            author1 = Author(name="Лев Толстой")
            author2 = Author(name="Федор Достоевский") 
            author3 = Author(name="Антон Чехов")
            
            db.add_all([author1, author2, author3])
            db.flush()  # Получаем ID авторов
            print(f"   Создано авторов: {len([author1, author2, author3])}")
            
            # Создаем категории
            print("📂 Создание категорий...")
            classic = Category(name="Классическая литература")
            drama = Category(name="Драма")
            philosophy = Category(name="Философия")
            
            db.add_all([classic, drama, philosophy])
            db.flush()  # Получаем ID категорий
            print(f"   Создано категорий: {len([classic, drama, philosophy])}")
            
            # Создаем аудиокниги
            print("📚 Создание аудиокниг...")
            audiobooks = [
                Audiobook(
                    title="Война и мир",
                    description="Эпический роман о войне 1812 года",
                    price=Decimal("299.99"),
                    author_id=author1.id,
                    cover_image_url="https://example.com/war_and_peace.jpg"
                ),
                Audiobook(
                    title="Преступление и наказание", 
                    description="Психологический роман о преступлении и его последствиях",
                    price=Decimal("199.99"),
                    author_id=author2.id,
                    cover_image_url="https://example.com/crime_punishment.jpg"
                ),
                Audiobook(
                    title="Вишневый сад",
                    description="Пьеса о уходящей эпохе русского дворянства",
                    price=Decimal("149.99"),
                    author_id=author3.id,
                    cover_image_url="https://example.com/cherry_orchard.jpg"
                ),
                Audiobook(
                    title="Анна Каренина",
                    description="Роман о любви и трагедии",
                    price=Decimal("249.99"),
                    author_id=author1.id,
                    cover_image_url="https://example.com/anna_karenina.jpg"
                ),
                Audiobook(
                    title="Братья Карамазовы",
                    description="Философский роман о семье и вере",
                    price=Decimal("279.99"),
                    author_id=author2.id,
                    cover_image_url="https://example.com/brothers_karamazov.jpg"
                )
            ]
            
            db.add_all(audiobooks)
            db.flush()  # Получаем ID аудиокниг
            print(f"   Создано аудиокниг: {len(audiobooks)}")
            
            # Добавляем категории к аудиокнигам
            print("🔗 Связывание аудиокниг с категориями...")
            audiobooks[0].categories.extend([classic, drama])      # Война и мир
            audiobooks[1].categories.extend([classic, philosophy]) # Преступление и наказание
            audiobooks[2].categories.append(drama)                 # Вишневый сад
            audiobooks[3].categories.extend([classic, drama])      # Анна Каренина
            audiobooks[4].categories.extend([classic, philosophy]) # Братья Карамазовы
            
            db.commit()
            
            print("✅ Тестовые данные добавлены успешно!")
            print(f"   - Авторов: {len([author1, author2, author3])}")
            print(f"   - Категорий: {len([classic, drama, philosophy])}")
            print(f"   - Аудиокниг: {len(audiobooks)}")
            
            # Показываем добавленные книги
            print("\n📚 Добавленные аудиокниги:")
            for book in audiobooks:
                print(f"   {book.id}. {book.title} - {book.price} руб. (автор: {book.author.name})")
            
    except Exception as e:
        print(f"❌ Ошибка при добавлении данных: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    return True

if __name__ == "__main__":
    success = add_test_data()
    if success:
        print("\n🎉 Готово! Теперь можно тестировать создание заказов")
        print("💡 Примеры ID аудиокниг для тестирования: 1, 2, 3, 4, 5")
    else:
        print("\n💥 Не удалось добавить тестовые данные")
        sys.exit(1) 