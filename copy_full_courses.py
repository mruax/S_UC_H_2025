#!/usr/bin/env python3
"""
Скрипт для копирования полного файла tagged_courses.json
Использование: python copy_full_courses.py
"""

import os
import shutil

def copy_courses_file():
    """Копирует полный файл tagged_courses.json в папку recommendations"""
    
    # Пути к файлам
    source_file = "recommendations/tagged_courses.json"  # Полный файл с 100+ курсами
    backup_file = "recommendations/tagged_courses_backup.json"
    
    # Проверяем, существует ли исходный файл
    if not os.path.exists(source_file):
        print("❌ Файл recommendations/tagged_courses.json не найден!")
        print("📝 Убедитесь, что полный файл находится в папке recommendations/")
        return False
    
    # Создаем бэкап если файл уже существует
    if os.path.exists(source_file):
        print(f"📦 Создание бэкапа: {backup_file}")
        shutil.copy2(source_file, backup_file)
        print(f"✅ Бэкап создан")
    
    print(f"\n📊 Информация о файле:")
    file_size = os.path.getsize(source_file)
    print(f"   Размер: {file_size / 1024:.2f} KB")
    
    # Проверяем JSON
    try:
        import json
        with open(source_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"   Количество курсов: {len(data)}")
            print(f"\n✅ Файл валидный и готов к использованию!")
            
            # Показываем несколько примеров курсов
            print(f"\n📚 Примеры курсов:")
            for i, course in enumerate(data[:3]):
                print(f"   {i+1}. {course['name']}")
                print(f"      Категория: {course['tags']['direction']['name']}")
                print(f"      Сложность: {course['tags']['difficulty']}")
                print()
            
            return True
            
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка в JSON файле: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Проверка файла курсов tagged_courses.json")
    print("=" * 60)
    print()
    
    success = copy_courses_file()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ ГОТОВО!")
        print("=" * 60)
        print("\nСледующие шаги:")
        print("1. Запустите docker-compose up -d")
        print("2. Курсы будут автоматически загружены при старте")
        print("3. Или запустите вручную: docker-compose exec web python manage.py create_demo_data")
    else:
        print("\n" + "=" * 60)
        print("❌ Возникли проблемы")
        print("=" * 60)
        print("\nСкопируйте полный файл tagged_courses.json в папку recommendations/")
