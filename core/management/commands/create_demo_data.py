from django.core.management.base import BaseCommand
from core.models import User, Course
import math
import json
import os

class Command(BaseCommand):
    help = 'Создает демо данные (курсы из tagged_courses.json)'

    def handle(self, *args, **kwargs):
        # Создаем админа если его нет
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                password='admin',
                email='admin@edu.com',
                role='admin'
            )
            self.stdout.write(self.style.SUCCESS('Создан админ: admin/admin'))
        
        # Создаем тестовых пользователей
        if not User.objects.filter(username='student1').exists():
            User.objects.create_user(
                username='student1',
                password='student1',
                email='student1@edu.com',
                role='student'
            )
            self.stdout.write(self.style.SUCCESS('Создан студент: student1/student1'))
        
        if not User.objects.filter(username='teacher1').exists():
            User.objects.create_user(
                username='teacher1',
                password='teacher1',
                email='teacher1@edu.com',
                role='teacher'
            )
            self.stdout.write(self.style.SUCCESS('Создан преподаватель: teacher1/teacher1'))
        
        # Создаем курсы если их нет
        if Course.objects.count() == 0:
            # Загружаем курсы из JSON файла
            json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 
                                     'recommendations', 'tagged_courses.json')
            
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    courses_json = json.load(f)
                
                self.stdout.write(self.style.SUCCESS(f'Загружено {len(courses_json)} курсов из JSON'))
                
                # Маппинг сложности
                difficulty_map = {
                    'Без опыта': 'beginner',
                    'Начальный': 'beginner',
                    'Продвинутый': 'advanced'
                }
                
                # Располагаем курсы на сфере
                radius = 5
                num_courses = len(courses_json)
                
                for i, course_json in enumerate(courses_json):
                    # Равномерное распределение на сфере (алгоритм Фибоначчи)
                    phi = math.acos(1 - 2 * (i + 0.5) / num_courses)
                    theta = math.pi * (1 + 5**0.5) * i
                    
                    x = radius * math.sin(phi) * math.cos(theta)
                    y = radius * math.sin(phi) * math.sin(theta)
                    z = radius * math.cos(phi)
                    
                    # Получаем данные из JSON
                    title = course_json.get('name', '')
                    description = course_json.get('description', '')
                    external_url = course_json.get('url', '')
                    
                    tags = course_json.get('tags', {})
                    direction = tags.get('direction', {})
                    category = direction.get('name', 'Общее')
                    area = direction.get('code', '')
                    
                    competencies = tags.get('competencies', [])
                    difficulty_ru = tags.get('difficulty', 'Начальный')
                    difficulty = difficulty_map.get(difficulty_ru, 'intermediate')
                    
                    # Генерируем moodle_id
                    moodle_id = f"COURSE_{i+1:03d}"
                    
                    # Определяем длительность на основе сложности
                    duration_map = {
                        'beginner': 30,
                        'intermediate': 45,
                        'advanced': 60
                    }
                    duration_hours = duration_map.get(difficulty, 40)
                    
                    # Создаем курс
                    Course.objects.create(
                        title=title,
                        description=description,
                        category=category,
                        moodle_id=moodle_id,
                        duration_hours=duration_hours,
                        difficulty=difficulty,
                        external_url=external_url,
                        area=area,
                        thematic_tags=competencies,
                        categories_tags=[],
                        attributes=[],
                        x_position=x,
                        y_position=y,
                        z_position=z
                    )
                
                self.stdout.write(self.style.SUCCESS(f'Создано {num_courses} курсов из tagged_courses.json'))
                
            except FileNotFoundError:
                self.stdout.write(self.style.ERROR(f'Файл не найден: {json_path}'))
                self.stdout.write(self.style.WARNING('Создаю базовые курсы...'))
                
                # Fallback: создаем базовые курсы
                self._create_basic_courses()
        
        else:
            self.stdout.write(self.style.WARNING('Курсы уже существуют в базе данных'))
    
    def _create_basic_courses(self):
        """Создает базовые курсы если JSON файл не найден"""
        basic_courses = [
            {
                'title': 'Python для начинающих',
                'description': 'Основы программирования на Python',
                'category': 'Программирование',
                'moodle_id': 'MOODLE_PY101',
                'duration_hours': 40,
                'difficulty': 'beginner'
            },
            {
                'title': 'Машинное обучение',
                'description': 'Введение в ML и нейронные сети',
                'category': 'Data Science',
                'moodle_id': 'MOODLE_ML201',
                'duration_hours': 60,
                'difficulty': 'intermediate'
            },
        ]
        
        radius = 5
        for i, course_data in enumerate(basic_courses):
            phi = math.acos(1 - 2 * (i + 0.5) / len(basic_courses))
            theta = math.pi * (1 + 5**0.5) * i
            
            x = radius * math.sin(phi) * math.cos(theta)
            y = radius * math.sin(phi) * math.sin(theta)
            z = radius * math.cos(phi)
            
            Course.objects.create(
                **course_data,
                x_position=x,
                y_position=y,
                z_position=z
            )
        
        self.stdout.write(self.style.SUCCESS(f'Создано {len(basic_courses)} базовых курсов'))