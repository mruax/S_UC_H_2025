"""
Парсер курсов из Stepik API и Coursera Dataset
"""

import requests
import pandas as pd
import time
from typing import List, Dict
import json


class CourseParser:
    def __init__(self):
        self.courses = []

    def parse_stepik(self, max_courses: int = 100) -> List[Dict]:
        """Парсинг курсов из Stepik API"""
        print("🔍 Парсинг курсов из Stepik...")

        stepik_courses = []
        page = 1

        while len(stepik_courses) < max_courses:
            try:
                url = "https://stepik.org/api/courses"
                params = {
                    'is_public': True,
                    'page': page,
                    'is_enabled': True
                }

                response = requests.get(url, params=params, timeout=10)

                if response.status_code != 200:
                    print(f"⚠️ Ошибка запроса: {response.status_code}")
                    break

                data = response.json()
                courses = data.get('courses', [])

                if not courses:
                    break

                for course in courses:
                    stepik_courses.append({
                        'id': f"stepik_{course['id']}",
                        'title': course.get('title', 'Без названия'),
                        'summary': course.get('summary', ''),
                        'description': course.get('description', '')[:500],  # Первые 500 символов
                        'difficulty': self._map_difficulty(course.get('difficulty', '')),
                        'language': course.get('language', 'ru'),
                        'learners_count': course.get('learners_count', 0),
                        'rating': course.get('review_summary', {}).get('average', 0),
                        'is_paid': course.get('is_paid', False),
                        'source': 'stepik',
                        'url': f"https://stepik.org/course/{course['id']}"
                    })

                print(f"  ✓ Страница {page}: получено {len(courses)} курсов")
                page += 1
                time.sleep(0.5)  # Чтобы не перегружать API

                if len(stepik_courses) >= max_courses:
                    break

            except Exception as e:
                print(f"❌ Ошибка на странице {page}: {e}")
                break

        print(f"✅ Stepik: спарсено {len(stepik_courses)} курсов\n")
        return stepik_courses[:max_courses]

    def parse_coursera_csv(self, csv_path: str = None) -> List[Dict]:
        """
        Загрузка и парсинг Coursera датасета
        Если csv_path не указан, создаёт пример данных
        """
        print("🔍 Загрузка Coursera датасета...")

        coursera_courses = []

        try:
            if csv_path and pd.io.common.file_exists(csv_path):
                df = pd.read_csv(csv_path)
            else:
                print("⚠️ CSV файл не найден, создаю примеры данных...")
                # Создаём примеры данных в формате Coursera
                df = pd.DataFrame({
                    'Course Name': [
                        'Machine Learning',
                        'Python for Data Science',
                        'Deep Learning Specialization',
                        'Web Development Bootcamp',
                        'Data Structures and Algorithms'
                    ],
                    'University': ['Stanford', 'IBM', 'DeepLearning.AI', 'Udemy', 'Princeton'],
                    'Difficulty Level': ['Intermediate', 'Beginner', 'Advanced', 'Beginner', 'Intermediate'],
                    'Course Rating': [4.9, 4.6, 4.8, 4.7, 4.5],
                    'Course Description': [
                        'Learn machine learning algorithms and applications',
                        'Introduction to Python programming for data analysis',
                        'Deep neural networks and their applications',
                        'Full-stack web development from scratch',
                        'Fundamental algorithms and data structures'
                    ],
                    'Skills': [
                        'Machine Learning, Python, Statistics',
                        'Python, Data Analysis, Pandas',
                        'Deep Learning, Neural Networks, TensorFlow',
                        'HTML, CSS, JavaScript, React',
                        'Algorithms, Data Structures, Python'
                    ]
                })

            for _, row in df.iterrows():
                coursera_courses.append({
                    'id': f"coursera_{hash(row.get('Course Name', ''))}",
                    'title': row.get('Course Name', 'Без названия'),
                    'summary': row.get('Course Description', '')[:200],
                    'description': row.get('Course Description', ''),
                    'difficulty': self._normalize_difficulty(row.get('Difficulty Level', 'intermediate')),
                    'language': 'en',
                    'learners_count': 0,  # Нет в датасете
                    'rating': float(row.get('Course Rating', 0)),
                    'is_paid': True,
                    'source': 'coursera',
                    'provider': row.get('University', 'Unknown'),
                    'skills': row.get('Skills', '').split(',') if pd.notna(row.get('Skills')) else [],
                    'url': f"https://www.coursera.org/learn/{row.get('Course Name', '').lower().replace(' ', '-')}"
                })

            print(f"✅ Coursera: загружено {len(coursera_courses)} курсов\n")

        except Exception as e:
            print(f"❌ Ошибка при загрузке Coursera: {e}\n")

        return coursera_courses

    def _map_difficulty(self, difficulty: str) -> str:
        """Маппинг уровня сложности Stepik"""
        difficulty_map = {
            'easy': 'beginner',
            'normal': 'intermediate',
            'hard': 'advanced'
        }
        return difficulty_map.get(difficulty.lower(), 'intermediate')

    def _normalize_difficulty(self, difficulty: str) -> str:
        """Нормализация уровня сложности"""
        difficulty = str(difficulty).lower()
        if 'begin' in difficulty:
            return 'beginner'
        elif 'adv' in difficulty:
            return 'advanced'
        else:
            return 'intermediate'

    def combine_and_save(self, stepik_courses: List[Dict], coursera_courses: List[Dict],
                         output_file: str = 'courses_combined.csv'):
        """Объединение и сохранение всех курсов"""
        print("💾 Объединение и сохранение данных...")

        all_courses = stepik_courses + coursera_courses
        df = pd.DataFrame(all_courses)

        # Сохраняем в CSV
        df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"✅ Сохранено в {output_file}")

        # Также сохраняем в JSON для удобства
        json_file = output_file.replace('.csv', '.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(all_courses, f, ensure_ascii=False, indent=2)
        print(f"✅ Сохранено в {json_file}")

        # Статистика
        self._print_statistics(df)

        return df

    def _print_statistics(self, df: pd.DataFrame):
        """Вывод статистики по спарсенным курсам"""
        print("\n" + "=" * 60)
        print("📊 СТАТИСТИКА")
        print("=" * 60)
        print(f"Всего курсов: {len(df)}")
        print(f"\nПо источникам:")
        print(df['source'].value_counts().to_string())
        print(f"\nПо сложности:")
        print(df['difficulty'].value_counts().to_string())
        print(f"\nПо языкам:")
        print(df['language'].value_counts().to_string())
        print(f"\nСредний рейтинг: {df['rating'].mean():.2f}")
        print("=" * 60)


def main():
    """Основная функция"""
    parser = CourseParser()

    # Парсим Stepik (100 курсов)
    stepik_courses = parser.parse_stepik(max_courses=100)

    # Загружаем Coursera (если есть CSV, иначе примеры)
    # Если у вас есть файл coursera_courses.csv, укажите путь:
    # coursera_courses = parser.parse_coursera_csv('coursera_courses.csv')
    coursera_courses = parser.parse_coursera_csv("coursera_courses.csv")

    # Объединяем и сохраняем
    df = parser.combine_and_save(stepik_courses, coursera_courses)

    print("\n🎉 Парсинг завершён!")
    print(f"📁 Результаты сохранены в:")
    print("   - courses_combined.csv")
    print("   - courses_combined.json")

    # Показываем примеры
    print("\n📝 Примеры спарсенных курсов:")
    print(df[['title', 'source', 'difficulty', 'rating']].head(10).to_string(index=False))


if __name__ == "__main__":
    main()
