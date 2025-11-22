# pip install natasha

from natasha import Doc, Segmenter, NewsEmbedding, NewsMorphTagger, MorphVocab
import re
import json
from typing import Dict, List, Tuple
from collections import Counter

# --- ПУТИ К ФАЙЛАМ ---
INPUT_COURSES = "courses.json"  # Файл с курсами
INPUT_SKILL_TREE = "grade_system\\skill_tree.json"  # Дерево навыков
OUTPUT_FILE = "tagged_courses.json"  # Результат

# --- Инициализация Natasha ---
segmenter = Segmenter()
emb = NewsEmbedding()
morph_tagger = NewsMorphTagger(emb)
morph_vocab = MorphVocab()

# --- Официальные направления подготовки (Приказ №1061 от 12.09.2013) ---
OFFICIAL_DIRECTIONS = {
    "01.00.00": {
        "name": "Математика и механика",
        "keywords": ["математика", "механика", "геометрия", "алгебра", "статистика", "теория вероятностей",
                     "математический анализ", "дифференциальное уравнение", "топология"]
    },
    "02.00.00": {
        "name": "Компьютерные и информационные науки",
        "keywords": ["компьютерные науки", "информационные науки", "теория информации", "алгоритм",
                     "искусственный интеллект", "machine learning", "data science", "анализ данных"]
    },
    "09.00.00": {
        "name": "Информатика и вычислительная техника",
        "keywords": ["программирование", "python", "java", "javascript", "c++", "разработка", "код",
                     "веб-разработка", "мобильная разработка", "база данных", "sql", "backend", "frontend",
                     "devops", "тестирование", "git", "api", "framework", "архитектура", "html", "css"]
    },
    "38.00.00": {
        "name": "Экономика и управление",
        "keywords": ["экономика", "менеджмент", "управление", "бизнес", "маркетинг", "финансы", "бухгалтерия",
                     "предпринимательство", "продажи", "логистика", "управление персоналом", "hr", "стратегия"]
    },
    "45.00.00": {
        "name": "Языкознание и литературоведение",
        "keywords": ["английский", "немецкий", "французский", "испанский", "китайский", "японский", "язык",
                     "грамматика", "лексика", "перевод", "лингвистика", "филология", "литература"]
    },
    "54.00.00": {
        "name": "Изобразительное и прикладные виды искусств",
        "keywords": ["дизайн", "графический дизайн", "ui", "ux", "веб-дизайн", "photoshop", "illustrator",
                     "figma", "3d", "моделирование", "blender", "анимация", "иллюстрация", "рисование"]
    },
    "42.00.00": {
        "name": "Средства массовой информации и информационно-библиотечное дело",
        "keywords": ["журналистика", "контент", "копирайтинг", "smm", "реклама", "связи с общественностью",
                     "pr", "медиа", "издательское дело", "редактирование"]
    },
    "44.00.00": {
        "name": "Образование и педагогические науки",
        "keywords": ["педагогика", "образование", "преподавание", "обучение", "методика", "воспитание",
                     "психология обучения", "дидактика"]
    },
    "11.00.00": {
        "name": "Электроника, радиотехника и системы связи",
        "keywords": ["электроника", "радиотехника", "связь", "телекоммуникации", "радио", "схемотехника"]
    },
    "49.00.00": {
        "name": "Физическая культура и спорт",
        "keywords": ["спорт", "физическая культура", "фитнес", "тренировка", "йога", "здоровье"]
    },
    "43.00.00": {
        "name": "Сервис и туризм",
        "keywords": ["туризм", "гостиничное дело", "сервис", "гостеприимство", "путешествия"]
    },
    "37.00.00": {
        "name": "Психологические науки",
        "keywords": ["психология", "эмоциональный интеллект", "психотерапия", "консультирование"]
    },
    "31.00.00": {
        "name": "Клиническая медицина",
        "keywords": ["медицина", "лечение", "диагностика", "терапия", "клиника", "здравоохранение"]
    },
    "10.00.00": {
        "name": "Информационная безопасность",
        "keywords": ["кибербезопасность", "защита информации", "безопасность", "шифрование", "этичный хакинг"]
    },
    "27.00.00": {
        "name": "Управление в технических системах",
        "keywords": ["автоматизация", "управление системами", "мехатроника", "робототехника", "iot", "arduino"]
    }
}

# --- Уровни сложности ---
DIFFICULTY_LEVELS = {
    "Без опыта": [
        "с нуля", "для начинающих", "начальный", "базовый", "основы", "введение",
        "без опыта", "новичок", "beginner", "не требуется опыт"
    ],
    "Начальный": [
        "базовые знания", "некоторый опыт", "elementary", "pre-intermediate",
        "начальные навыки", "знание основ"
    ],
    "Продвинутый": [
        "продвинутый", "advanced", "профессионал", "эксперт", "глубокие знания",
        "требуется опыт", "intermediate", "upper-intermediate", "углубленный"
    ]
}


class SkillTreeProcessor:
    """Обработка дерева навыков для поиска компетенций"""

    def __init__(self, skill_tree_path: str):
        with open(skill_tree_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.skill_tree = data.get('skills_tree', {})
        self.flat_skills = self._flatten_tree()

    def _flatten_tree(self) -> List[Dict]:
        """Преобразуем дерево в плоский список навыков с ключевыми словами"""
        flat_list = []

        def traverse(node, parent_keywords=None):
            if parent_keywords is None:
                parent_keywords = []

            name = node.get('name', '')
            code = node.get('code', '')
            description = node.get('description', '')

            # Извлекаем ключевые слова из названия и описания
            keywords = parent_keywords.copy()
            keywords.extend(self._extract_keywords(name))
            keywords.extend(self._extract_keywords(description))

            skill_info = {
                'name': name,
                'code': code,
                'description': description,
                'keywords': list(set([kw.lower() for kw in keywords if kw]))
            }

            flat_list.append(skill_info)

            # Рекурсивно обходим детей
            children = node.get('children', {})
            for child_key, child_node in children.items():
                traverse(child_node, keywords)

        # Обходим все верхнеуровневые категории
        for category_key, category_node in self.skill_tree.items():
            traverse(category_node)

        return flat_list

    def _extract_keywords(self, text: str) -> List[str]:
        """Извлекаем ключевые слова из текста"""
        if not text:
            return []

        # Убираем знаки препинания и разбиваем на слова
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)

        # Фильтруем стоп-слова
        stop_words = {'и', 'в', 'на', 'с', 'для', 'по', 'о', 'об', 'из', 'к', 'а', 'но'}
        keywords = [w for w in words if w not in stop_words and len(w) > 2]

        return keywords

    def find_matching_skills(self, title: str, description: str, max_skills: int = 7) -> List[Dict]:
        """Находим подходящие навыки из дерева на основе текста курса"""
        full_text = f"{title} {description}".lower()

        skill_scores = []

        for skill in self.flat_skills:
            score = 0
            matched_keywords = []

            # Проверяем вхождение названия навыка в текст (более точная проверка)
            skill_name_lower = skill['name'].lower()
            skill_words = skill_name_lower.split()

            # Если название навыка полностью есть в тексте - большой бонус
            if skill_name_lower in full_text:
                score += 10
                matched_keywords.append(skill_name_lower)
            # Или если большинство слов из названия есть в тексте
            elif len(skill_words) > 1:
                words_found = sum(1 for word in skill_words if word in full_text and len(word) > 2)
                if words_found >= len(skill_words) * 0.6:  # 60% слов найдено
                    score += 5
                    matched_keywords.extend(skill_words)

            # Считаем релевантность на основе ключевых слов
            for keyword in skill['keywords']:
                if len(keyword) < 3:  # Игнорируем короткие слова
                    continue

                if keyword in full_text:
                    # Точное совпадение слова
                    if f" {keyword} " in f" {full_text} " or full_text.startswith(keyword) or full_text.endswith(
                            keyword):
                        score += 2
                        matched_keywords.append(keyword)
                    # Подстрока
                    else:
                        score += 0.5

            if score > 0:
                skill_scores.append({
                    'skill': skill,
                    'score': score,
                    'matched_keywords': list(set(matched_keywords))
                })

        # Сортируем по релевантности
        skill_scores.sort(key=lambda x: x['score'], reverse=True)

        # Фильтруем - берем только те, у которых score >= 3 (достаточно релевантные)
        filtered_skills = [item for item in skill_scores if item['score'] >= 3]

        # Возвращаем топ навыков
        return [item['skill'] for item in filtered_skills[:max_skills]]


class CourseTagGenerator:
    def __init__(self, skill_tree_processor: SkillTreeProcessor):
        self.segmenter = segmenter
        self.morph_tagger = morph_tagger
        self.morph_vocab = morph_vocab
        self.skill_tree = skill_tree_processor

    def calculate_relevance(self, text: str, keywords: List[str]) -> float:
        """Вычисляем релевантность текста к набору ключевых слов"""
        text_lower = text.lower()
        score = 0

        for keyword in keywords:
            keyword_lower = keyword.lower()
            if f" {keyword_lower} " in f" {text_lower} ":
                score += 3
            elif keyword_lower in text_lower:
                score += 1

        return score

    def determine_direction(self, title: str, description: str) -> str:
        """Определяем направление подготовки"""
        full_text = f"{title} {description}".lower()

        direction_scores = {}

        for code, data in OFFICIAL_DIRECTIONS.items():
            score = self.calculate_relevance(full_text, data["keywords"])
            if score > 0:
                direction_scores[code] = score

        if direction_scores:
            return max(direction_scores, key=direction_scores.get)

        return "44.00.00"

    def extract_competencies(self, title: str, description: str) -> List[str]:
        """Извлекаем компетенции ТОЛЬКО из дерева навыков"""
        # Ищем навыки в дереве
        matching_skills = self.skill_tree.find_matching_skills(title, description, max_skills=7)

        # Формируем список компетенций ТОЛЬКО из найденных навыков
        competencies = []
        for skill in matching_skills:
            competency_name = skill['name']
            if competency_name and competency_name not in competencies:
                competencies.append(competency_name)

        # Если не нашли НИЧЕГО - возвращаем пустой список
        # НЕ добавляем дефолтные компетенции
        return competencies[:7]

    def determine_difficulty(self, title: str, description: str) -> str:
        """Определяем уровень сложности"""
        full_text = f"{title} {description}".lower()

        scores = {}
        for level, keywords in DIFFICULTY_LEVELS.items():
            score = sum(1 for keyword in keywords if keyword in full_text)
            scores[level] = score

        if scores and max(scores.values()) > 0:
            return max(scores, key=scores.get)

        return "Начальный"

    def generate_tags(self, course: Dict) -> Dict:
        """Генерация всех тегов для курса"""
        title = course.get('name', '')
        description = course.get('description', '')
        url = course.get('url', '')

        direction_code = self.determine_direction(title, description)
        competencies = self.extract_competencies(title, description)
        difficulty = self.determine_difficulty(title, description)

        return {
            "name": title,
            "description": description,
            "url": url,
            "tags": {
                "direction": {
                    "code": direction_code,
                    "name": OFFICIAL_DIRECTIONS[direction_code]["name"]
                },
                "competencies": competencies,  # Может быть пустым списком!
                "difficulty": difficulty
            }
        }


def process_courses(courses_file: str, skill_tree_file: str, output_file: str):
    """Обработка курсов и сохранение результата"""
    print(f"📖 Загрузка дерева навыков из {skill_tree_file}...")
    skill_processor = SkillTreeProcessor(skill_tree_file)
    print(f"✅ Загружено навыков: {len(skill_processor.flat_skills)}\n")

    print(f"📖 Загрузка курсов из {courses_file}...")
    with open(courses_file, 'r', encoding='utf-8') as f:
        courses = json.load(f)

    print(f"✅ Найдено курсов: {len(courses)}\n")
    print("🤖 Начинаем тегирование...\n")

    generator = CourseTagGenerator(skill_processor)
    tagged_courses = []
    courses_without_competencies = []

    for i, course in enumerate(courses, 1):
        if i <= 10 or i % 20 == 0:
            print(f"[{i}/{len(courses)}] {course['name'][:50]}...")
        tagged_course = generator.generate_tags(course)
        tagged_courses.append(tagged_course)

        # Считаем курсы без компетенций
        if not tagged_course['tags']['competencies']:
            courses_without_competencies.append(course['name'])

    print(f"\n💾 Сохранение в {output_file}...")

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(tagged_courses, f, ensure_ascii=False, indent=2)

    print("✅ Готово!\n")

    # Статистика
    direction_counter = Counter(c['tags']['direction']['code'] for c in tagged_courses)
    difficulty_counter = Counter(c['tags']['difficulty'] for c in tagged_courses)

    print("=" * 80)
    print("СТАТИСТИКА")
    print("=" * 80)

    print("\n📊 Распределение по направлениям (топ-10):")
    for code, count in direction_counter.most_common(10):
        print(f"  {code} {OFFICIAL_DIRECTIONS[code]['name']}: {count}")

    print("\n📈 Распределение по сложности:")
    for difficulty, count in difficulty_counter.most_common():
        print(f"  {difficulty}: {count}")

    # Курсы без компетенций
    print(f"\n⚠️  Курсы без найденных компетенций: {len(courses_without_competencies)}")
    if courses_without_competencies:
        print("   (для этих курсов нужно расширить дерево навыков)")
        for name in courses_without_competencies[:5]:
            print(f"   • {name}")
        if len(courses_without_competencies) > 5:
            print(f"   ... и еще {len(courses_without_competencies) - 5}")

    print("\n" + "=" * 80)
    print("ПРИМЕРЫ КОМПЕТЕНЦИЙ")
    print("=" * 80)

    # Показываем примеры с компетенциями
    examples_shown = 0
    for i, course in enumerate(tagged_courses):
        if course['tags']['competencies']:
            print(f"\n📚 {course['name']}")
            print(f"   🎓 Направление: {course['tags']['direction']['code']} - {course['tags']['direction']['name']}")
            print(f"   📊 Сложность: {course['tags']['difficulty']}")
            print(f"   ✨ Компетенции:")
            for comp in course['tags']['competencies']:
                print(f"      • {comp}")
            examples_shown += 1
            if examples_shown >= 5:
                break


if __name__ == "__main__":
    process_courses(INPUT_COURSES, INPUT_SKILL_TREE, OUTPUT_FILE)
