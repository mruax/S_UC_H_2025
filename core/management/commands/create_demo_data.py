from django.core.management.base import BaseCommand
from core.models import User, Course
import math

class Command(BaseCommand):
    help = 'Создает демо данные (курсы из "Moodle")'

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
            courses_data = [
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
                {
                    'title': 'Веб-разработка Django',
                    'description': 'Создание веб-приложений на Django',
                    'category': 'Программирование',
                    'moodle_id': 'MOODLE_DJANGO301',
                    'duration_hours': 50,
                    'difficulty': 'intermediate'
                },
                {
                    'title': 'Базы данных PostgreSQL',
                    'description': 'Проектирование и оптимизация БД',
                    'category': 'Базы данных',
                    'moodle_id': 'MOODLE_DB101',
                    'duration_hours': 35,
                    'difficulty': 'beginner'
                },
                {
                    'title': 'Алгоритмы и структуры данных',
                    'description': 'Основные алгоритмы и их применение',
                    'category': 'Программирование',
                    'moodle_id': 'MOODLE_ALG201',
                    'duration_hours': 45,
                    'difficulty': 'intermediate'
                },
                {
                    'title': 'Docker и контейнеризация',
                    'description': 'Работа с Docker и оркестрация',
                    'category': 'DevOps',
                    'moodle_id': 'MOODLE_DOCKER101',
                    'duration_hours': 30,
                    'difficulty': 'intermediate'
                },
                {
                    'title': 'React и современный фронтенд',
                    'description': 'Разработка интерфейсов на React',
                    'category': 'Фронтенд',
                    'moodle_id': 'MOODLE_REACT301',
                    'duration_hours': 55,
                    'difficulty': 'intermediate'
                },
                {
                    'title': 'Тестирование ПО',
                    'description': 'Unit-тесты, интеграционное тестирование',
                    'category': 'Тестирование',
                    'moodle_id': 'MOODLE_TEST101',
                    'duration_hours': 25,
                    'difficulty': 'beginner'
                },
                {
                    'title': 'Компьютерное зрение',
                    'description': 'Обработка изображений и CV',
                    'category': 'Data Science',
                    'moodle_id': 'MOODLE_CV401',
                    'duration_hours': 65,
                    'difficulty': 'advanced'
                },
                {
                    'title': 'Блокчейн и криптовалюты',
                    'description': 'Основы блокчейн технологий',
                    'category': 'Блокчейн',
                    'moodle_id': 'MOODLE_BLOCK201',
                    'duration_hours': 40,
                    'difficulty': 'intermediate'
                },
                {
                    'title': 'UX/UI дизайн',
                    'description': 'Проектирование пользовательских интерфейсов',
                    'category': 'Дизайн',
                    'moodle_id': 'MOODLE_UX101',
                    'duration_hours': 35,
                    'difficulty': 'beginner'
                },
                {
                    'title': 'Кибербезопасность',
                    'description': 'Основы информационной безопасности',
                    'category': 'Безопасность',
                    'moodle_id': 'MOODLE_SEC201',
                    'duration_hours': 50,
                    'difficulty': 'intermediate'
                },
            ]
            
            # Располагаем курсы на сфере
            radius = 5
            num_courses = len(courses_data)
            
            for i, course_data in enumerate(courses_data):
                # Равномерное распределение на сфере (алгоритм Фибоначчи)
                phi = math.acos(1 - 2 * (i + 0.5) / num_courses)
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
            
            self.stdout.write(self.style.SUCCESS(f'Создано {num_courses} курсов'))
