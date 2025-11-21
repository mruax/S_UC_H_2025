# pip install natasha

from natasha import Doc, Segmenter, NewsEmbedding, NewsMorphTagger, MorphVocab
from collections import Counter, defaultdict
import re
import json
from typing import Dict, List, Set, Tuple, Optional
from pathlib import Path

# --- Инициализация Natasha ---
segmenter = Segmenter()
emb = NewsEmbedding()
morph_tagger = NewsMorphTagger(emb)
morph_vocab = MorphVocab()

# --- Стоп-слова ---
STOPWORDS = {
    "курс", "для", "изучение", "основа", "введение", "по", "урок", "занятие",
    "обучение", "год", "это", "быть", "который", "мочь", "весь", "свой", "наш",
    "ваш", "тот", "этот", "мой", "твой", "его", "её", "наш", "учить", "научиться",
    "получить", "узнать", "понять", "освоить", "один", "два", "три"
}

# Отглагольные существительные и процессы
PROCESS_WORDS = {
    "изучение", "создание", "разработка", "применение", "использование", "внедрение",
    "освоение", "понимание", "знакомство", "погружение", "работа", "обучение",
    "реализация", "оптимизация", "проектирование", "построение", "формирование"
}

# Общие прилагательные и слова сложности
GENERIC_ADJECTIVES = {
    "основной", "главный", "важный", "новый", "старый", "большой", "малый",
    "хороший", "плохой", "простой", "сложный", "полный", "частичный", "общий",
    "специальный", "различный", "разный", "первый", "последний", "современный",
    "практический", "теоретический", "глубокий", "поверхностный", "начинающий",
    "продвинутый", "базовый", "средний", "начальный", "профессиональный"
}

# --- Иерархия областей ---
AREAS = {
    "программирование": {
        "keywords": ["программирование", "разработка", "код", "coding", "programming", "python", "java", "javascript",
                     "c++", "веб-разработка"],
        "priority": 10,
        "related_words": ["разработчик", "программист", "developer", "сайт", "приложение"],
        "default_categories": ["алгоритмы", "синтаксис языка"]
    },
    "данные": {
        "keywords": ["данные", "data", "аналитика", "analytics", "анализ данных", "big data", "визуализация данных"],
        "priority": 9,
        "related_words": ["аналитик", "analyst", "обработка"],
        "default_categories": ["анализ данных", "визуализация"]
    },
    "машинное обучение": {
        "keywords": ["машинный", "обучение", "ml", "machine learning", "нейросеть", "ai", "искусственный интеллект",
                     "нейронный"],
        "priority": 9,
        "related_words": ["модель", "алгоритм", "предсказание"],
        "default_categories": ["модели", "алгоритмы"]
    },
    "веб-разработка": {
        "keywords": ["веб", "web", "сайт", "frontend", "backend", "fullstack", "react", "node", "html", "css"],
        "priority": 8,
        "related_words": ["браузер", "http", "интернет"],
        "default_categories": ["веб-технологии", "фронтенд"]
    },
    "математика": {
        "keywords": ["математика", "алгебра", "геометрия", "math", "матан", "статистика", "математический анализ",
                     "анализ"],
        "priority": 7,
        "related_words": ["формула", "уравнение", "теорема", "функция"],
        "default_categories": ["математический анализ", "теория"]
    },
    "дизайн": {
        "keywords": ["дизайн", "design", "графика", "ui", "ux", "figma", "photoshop", "интерфейс"],
        "priority": 7,
        "related_words": ["макет", "прототип", "композиция"],
        "default_categories": ["UI/UX дизайн", "визуальный дизайн"]
    },
    "бизнес": {
        "keywords": ["бизнес", "business", "менеджмент", "управление", "маркетинг", "продажа", "финансы", "экономика"],
        "priority": 6,
        "related_words": ["стратегия", "продажи", "финансы", "бюджет"],
        "default_categories": ["менеджмент", "стратегия"]
    },
    "языки": {
        "keywords": ["английский", "немецкий", "испанский", "китайский", "французский", "язык", "грамматика",
                     "лексика"],
        "priority": 8,
        "related_words": ["произношение", "диалог", "разговор", "иероглиф"],
        "default_categories": ["грамматика", "лексика"]
    },
    "личное развитие": {
        "keywords": ["продуктивность", "тайм-менеджмент", "мотивация", "развитие", "навык", "коммуникация"],
        "priority": 5,
        "related_words": ["эффективность", "цель", "привычка"],
        "default_categories": ["soft skills", "самоорганизация"]
    }
}

# --- Технологии и инструменты ---
TECHNOLOGIES = {
    "python": ["python", "питон"],
    "java": ["java", "джава"],
    "javascript": ["javascript", "js", "typescript", "node"],
    "c++": ["c++", "cpp", "си++"],
    "sql": ["sql", "база данных", "database", "postgresql", "mysql"],
    "pandas": ["pandas"],
    "numpy": ["numpy"],
    "tensorflow": ["tensorflow", "tf"],
    "pytorch": ["pytorch"],
    "react": ["react", "реакт"],
    "django": ["django", "джанго"],
    "flask": ["flask"],
    "docker": ["docker", "контейнер"],
    "git": ["git", "github", "gitlab"],
    "html/css": ["html", "css", "верстка"],
    "figma": ["figma"],
    "excel": ["excel", "таблица"],
}

# --- Предметные концепции ---
DOMAIN_CONCEPTS = {
    "нейронные сети": ["нейронный сеть", "нейросеть", "neural network"],
    "API": ["api", "интерфейс программирования"],
    "базы данных": ["база данных", "database", "бд"],
    "алгоритмы": ["алгоритм"],
    "структуры данных": ["структура данных"],
    "веб-приложения": ["веб приложение", "web application"],
    "интерфейсы": ["интерфейс", "ui", "gui"],
    "прототипы": ["прототип", "prototype"],
    "макеты": ["макет", "layout"],
    "модели": ["модель", "model"],
    "пределы": ["предел", "limit"],
    "производные": ["производный", "derivative"],
    "интегралы": ["интеграл", "integral"],
    "компоненты": ["компонент", "component"],
    "упражнения": ["упражнение", "задача", "задание"],
    "грамматика": ["грамматика", "grammar"],
    "лексика": ["лексика", "словарь", "vocabulary"],
    "произношение": ["произношение", "фонетика"],
    "финансы": ["финансы", "деньги", "бюджет", "инвестиция"],
    "бухгалтерия": ["бухгалтерия", "учет", "баланс"],
}

# --- Категории ---
CATEGORIES = {
    "анализ данных": ["анализ данных", "data analysis", "визуализация", "обработка данных", "pandas", "numpy"],
    "алгоритмы": ["алгоритм", "структура данных", "сортировка", "граф", "дерево"],
    "веб-технологии": ["веб", "http", "api", "rest", "сервер", "клиент", "веб приложение"],
    "мобильная разработка": ["мобильный", "android", "ios", "mobile"],
    "devops": ["devops", "ci/cd", "deployment", "автоматизация", "docker", "kubernetes"],
    "тестирование": ["тестирование", "testing", "qa", "тест", "pytest"],
    "безопасность": ["безопасность", "security", "защита", "шифрование"],
    "базы данных": ["база данных", "sql", "nosql", "запрос", "таблица"],
    "проектирование": ["проектирование", "архитектура", "паттерн", "design pattern"],
    "нейронные сети": ["нейронный", "нейросеть", "deep learning", "глубокий обучение"],
    "математический анализ": ["математический анализ", "матан", "предел", "производный", "интеграл"],
    "UI/UX дизайн": ["ui", "ux", "интерфейс", "пользовательский опыт", "юзабилити"],
    "прототипирование": ["прототип", "макет", "wireframe"],
    "синтаксис языка": ["синтаксис", "грамматика", "конструкция"],
    "визуализация": ["визуализация", "график", "диаграмма", "plotting"],
    "фронтенд": ["frontend", "фронтенд", "клиентский"],
    "бэкенд": ["backend", "бэкенд", "серверный"],
    "грамматика": ["грамматика", "времена", "падеж", "склонение"],
    "лексика": ["лексика", "словарный запас", "vocabulary"],
    "разговорная практика": ["разговор", "диалог", "общение", "речь"],
    "финансовое планирование": ["планирование", "бюджет", "инвестиция", "пенсия"],
    "управление проектами": ["управление проект", "pmi", "планирование", "риск"],
    "soft skills": ["коммуникация", "лидерство", "управление команда", "presentation"],
    "продуктивность": ["продуктивность", "эффективность", "время", "планирование"],
}

# --- Атрибуты ---
ATTRIBUTES = {
    "практический": ["практический", "проект", "hands-on", "практика", "задача", "упражнение", "задание"],
    "интенсивный": ["интенсивный", "bootcamp", "буткемп", "ускоренный", "интенсив"],
    "краткий": ["краткий", "мини", "быстрый", "short", "экспресс", "компактный"],
    "теоретический": ["теория", "лекция", "обзор", "фундаментальный", "академический"],
    "сертификация": ["сертификат", "certification", "аттестация", "диплом"],
    "интерактивный": ["интерактивный", "interactive", "живой", "онлайн-занятие"],
}

# --- Уровни сложности ---
DIFFICULTY = {
    "начальный": ["начальный", "введение", "основы", "начинающий", "базовый", "beginner", "basic", "нуль", "с нуля"],
    "средний": ["средний", "intermediate", "продолжающий", "средний уровень"],
    "продвинутый": ["продвинутый", "advanced", "эксперт", "профессиональный", "глубокий", "углубленный"]
}

# --- Индикаторы сложности по контексту ---
DIFFICULTY_INDICATORS = {
    "начальный": ["основа", "введение", "начало", "первый шаг", "знакомство", "базовый"],
    "средний": ["применение", "реализация", "создание"],
    "продвинутый": ["оптимизация", "масштабирование", "архитектура", "профессиональный"]
}


class CourseTagGenerator:
    def __init__(self):
        self.segmenter = segmenter
        self.morph_tagger = morph_tagger
        self.morph_vocab = morph_vocab

    def analyze_tokens(self, text: str) -> List[Tuple[str, str]]:
        """Анализ токенов с определением части речи"""
        doc = Doc(text)
        doc.segment(self.segmenter)
        doc.tag_morph(self.morph_tagger)

        tokens_info = []
        for token in doc.tokens:
            token.lemmatize(self.morph_vocab)
            lemma = token.lemma.lower()
            pos = token.pos
            if len(lemma) > 2 and lemma not in STOPWORDS and lemma.isalpha():
                tokens_info.append((lemma, pos))

        return tokens_info

    def extract_meaningful_phrases(self, text: str) -> List[str]:
        """Извлекаем только ОСМЫСЛЕННЫЕ словосочетания"""
        doc = Doc(text)
        doc.segment(self.segmenter)
        doc.tag_morph(self.morph_tagger)

        for token in doc.tokens:
            token.lemmatize(self.morph_vocab)

        phrases = []
        tokens = [t for t in doc.tokens if len(t.lemma) > 2 and t.lemma.lower() not in STOPWORDS]

        for i in range(len(tokens) - 1):
            current = tokens[i]
            next_token = tokens[i + 1]

            current_lemma = current.lemma.lower()
            next_lemma = next_token.lemma.lower()

            if current_lemma in GENERIC_ADJECTIVES:
                continue

            if current_lemma in PROCESS_WORDS:
                continue

            if current.pos == 'NOUN' and next_token.pos == 'NOUN':
                if next_lemma not in PROCESS_WORDS and next_lemma not in GENERIC_ADJECTIVES:
                    phrase = f"{current_lemma} {next_lemma}"
                    phrases.append(phrase)

            elif current.pos == 'ADJ' and next_token.pos == 'NOUN':
                if next_lemma not in PROCESS_WORDS:
                    phrase = f"{current_lemma} {next_lemma}"
                    phrases.append(phrase)

        return phrases

    def normalize_text(self, text: str) -> List[str]:
        """Нормализация текста: только существительные и значимые термины"""
        tokens_info = self.analyze_tokens(text)

        normalized = []
        for lemma, pos in tokens_info:
            if lemma in PROCESS_WORDS or lemma in GENERIC_ADJECTIVES:
                continue

            if pos in ['NOUN', 'PROPN'] or any(lemma in techs for techs in TECHNOLOGIES.values()):
                normalized.append(lemma)

        return normalized

    def extract_phrases(self, text: str) -> List[str]:
        """Извлекаем биграммы и триграммы"""
        words = re.findall(r'\w+', text.lower())
        phrases = []

        phrases.extend(words)

        for i in range(len(words) - 1):
            phrases.append(f"{words[i]} {words[i + 1]}")

        for i in range(len(words) - 2):
            phrases.append(f"{words[i]} {words[i + 1]} {words[i + 2]}")

        return phrases

    def score_match(self, text: str, keywords: List[str]) -> float:
        """Вычисляем релевантность текста к набору ключевых слов"""
        text_lower = text.lower()
        phrases = self.extract_phrases(text)

        score = 0
        for keyword in keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in text_lower.split():
                score += 2
            elif any(keyword_lower in phrase for phrase in phrases):
                score += 1

        return score

    def is_similar_or_contains(self, tag1: str, tag2: str) -> bool:
        """Проверяем, похожи ли теги или один содержится в другом"""
        tag1_lower = tag1.lower()
        tag2_lower = tag2.lower()

        if tag1_lower in tag2_lower or tag2_lower in tag1_lower:
            return True

        words1 = set(tag1_lower.split())
        words2 = set(tag2_lower.split())

        if len(words1) > 0 and len(words2) > 0:
            intersection = words1.intersection(words2)
            min_len = min(len(words1), len(words2))
            if len(intersection) / min_len > 0.5:
                return True

        return False

    def determine_area(self, title: str, description: str) -> str:
        """Определяем основную область курса"""
        full_text = f"{title} {description}"

        scores = {}
        for area, data in AREAS.items():
            match_score = self.score_match(full_text, data["keywords"])
            related_score = self.score_match(full_text, data.get("related_words", []))
            scores[area] = (match_score + related_score * 0.5) * data["priority"]

        if scores and max(scores.values()) > 0:
            return max(scores, key=scores.get)

        for tech, keywords in TECHNOLOGIES.items():
            if self.score_match(full_text, keywords) > 0:
                if tech in ["python", "java", "javascript", "c++"]:
                    return "программирование"
                elif tech in ["tensorflow", "pytorch"]:
                    return "машинное обучение"
                elif tech in ["react", "html/css", "django", "flask"]:
                    return "веб-разработка"
                elif tech in ["sql", "pandas", "numpy"]:
                    return "данные"
                elif tech in ["figma"]:
                    return "дизайн"

        tech_indicators = ["программ", "код", "разработ", "техн", "it"]
        if any(ind in full_text.lower() for ind in tech_indicators):
            return "программирование"

        return "общее обучение"

    def determine_thematic_tags(self, title: str, description: str, area: str) -> List[str]:
        """Определяем тематические теги: технологии + предметные концепции"""
        full_text = f"{title} {description}"

        tags = []
        excluded_tags = [area] if area else []

        # 1. Ищем технологии
        tech_scores = {}
        for tech, keywords in TECHNOLOGIES.items():
            score = self.score_match(full_text, keywords)
            if score > 0:
                tech_scores[tech] = score

        if tech_scores:
            sorted_techs = sorted(tech_scores.items(), key=lambda x: x[1], reverse=True)
            for tech, _ in sorted_techs:
                if not any(self.is_similar_or_contains(tech, ex) for ex in excluded_tags):
                    tags.append(tech)
                if len(tags) >= 2:
                    break

        # 2. Ищем предметные концепции
        if len(tags) < 3:
            concept_scores = {}
            for concept, keywords in DOMAIN_CONCEPTS.items():
                score = self.score_match(full_text, keywords)
                if score > 0:
                    concept_scores[concept] = score

            if concept_scores:
                sorted_concepts = sorted(concept_scores.items(), key=lambda x: x[1], reverse=True)
                for concept, _ in sorted_concepts:
                    if len(tags) >= 3:
                        break
                    if not any(self.is_similar_or_contains(concept, ex) for ex in excluded_tags + tags):
                        tags.append(concept)

        # 3. Извлекаем осмысленные словосочетания
        if len(tags) < 3:
            noun_phrases = self.extract_meaningful_phrases(full_text)

            for phrase in noun_phrases:
                if len(tags) >= 3:
                    break
                if not any(self.is_similar_or_contains(phrase, ex) for ex in excluded_tags + tags):
                    tags.append(phrase)

        # 4. Последний fallback: существительные
        if len(tags) < 1:
            normalized = self.normalize_text(full_text)

            if area and area in AREAS:
                area_words = set()
                for keyword in AREAS[area]["keywords"]:
                    area_words.update(keyword.lower().split())
                normalized = [w for w in normalized if w not in area_words]

            if normalized:
                counter = Counter(normalized)
                for word, _ in counter.most_common(3):
                    if not any(self.is_similar_or_contains(word, ex) for ex in excluded_tags + tags):
                        tags.append(word)
                    if len(tags) >= 3:
                        break

        # Финальный fallback
        if not tags:
            title_words = self.normalize_text(title)
            if title_words:
                tags = [title_words[0]]
            else:
                tags = ["разное"]

        return tags[:3]

    def determine_categories(self, title: str, description: str, area: str, thematic_tags: List[str]) -> List[str]:
        """Определяем категории с умными fallback'ами"""
        full_text = f"{title} {description}"

        excluded = [area] + thematic_tags

        scores = {}
        for category, keywords in CATEGORIES.items():
            scores[category] = self.score_match(full_text, keywords)

        sorted_categories = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        categories = []

        # Берём категории с положительным скором
        for cat, score in sorted_categories:
            if score > 0 and not any(self.is_similar_or_contains(cat, ex) for ex in excluded + categories):
                categories.append(cat)
            if len(categories) >= 3:
                break

        # Fallback 1: ищем предметные концепции
        if not categories:
            for concept, keywords in DOMAIN_CONCEPTS.items():
                if self.score_match(full_text, keywords) > 0:
                    if not any(self.is_similar_or_contains(concept, ex) for ex in excluded + categories):
                        categories.append(concept)
                    if len(categories) >= 3:
                        break

        # Fallback 2: используем дефолтные категории для области
        if not categories and area in AREAS:
            default_cats = AREAS[area].get("default_categories", [])
            for cat in default_cats:
                if not any(self.is_similar_or_contains(cat, ex) for ex in excluded + categories):
                    categories.append(cat)
                if len(categories) >= 3:
                    break

        # Fallback 3: извлекаем осмысленные словосочетания из описания
        if not categories:
            noun_phrases = self.extract_meaningful_phrases(description)
            for phrase in noun_phrases:
                if not any(self.is_similar_or_contains(phrase, ex) for ex in excluded + categories):
                    categories.append(phrase)
                if len(categories) >= 1:
                    break

        # Fallback 4: берём самые частые существительные
        if not categories:
            normalized = self.normalize_text(description)
            if normalized:
                counter = Counter(normalized)
                for word, _ in counter.most_common(3):
                    if not any(self.is_similar_or_contains(word, ex) for ex in excluded + categories):
                        categories.append(word)
                    if len(categories) >= 1:
                        break

        # Последний fallback: используем thematic_tags как категории
        if not categories and thematic_tags:
            categories = [thematic_tags[0]]

        return categories[:3]

    def determine_attributes(self, title: str, description: str) -> List[str]:
        """Определяем атрибуты курса"""
        full_text = f"{title} {description}"

        attrs = []
        scores = {}

        for attr, keywords in ATTRIBUTES.items():
            score = self.score_match(full_text, keywords)
            if score > 0:
                scores[attr] = score

        if scores:
            attrs = [attr for attr, _ in sorted(scores.items(), key=lambda x: x[1], reverse=True)]

        if not attrs:
            practice_words = ["делать", "создать", "разработать", "проект", "применить", "реализовать", "упражнение",
                              "задание", "задача"]
            if any(word in full_text.lower() for word in practice_words):
                attrs.append("практический")
            elif any(word in full_text.lower() for word in ["теория", "концепция", "понимание", "изучение"]):
                attrs.append("теоретический")
            else:
                if "применение" in full_text.lower() or "использование" in full_text.lower():
                    attrs.append("практический")
                else:
                    attrs.append("теоретический")

        return attrs

    def determine_difficulty(self, title: str, description: str) -> str:
        """Определяем уровень сложности"""
        full_text = f"{title} {description}"

        scores = {}
        for level, keywords in DIFFICULTY.items():
            scores[level] = self.score_match(full_text, keywords)

        for level, indicators in DIFFICULTY_INDICATORS.items():
            indicator_score = self.score_match(full_text, indicators)
            scores[level] = scores.get(level, 0) + indicator_score * 0.5

        if scores and max(scores.values()) > 0:
            return max(scores, key=scores.get)

        full_lower = full_text.lower()

        if any(word in full_lower for word in ["начин", "основ", "введение", "базов", "первый"]):
            return "начальный"

        if any(word in full_lower for word in ["продвин", "эксперт", "сложн", "профессионал"]):
            return "продвинутый"

        return "средний"

    def generate_tags(self, title: str, description: str) -> Dict:
        """Главная функция: генерация всех тегов с дедупликацией"""
        area = self.determine_area(title, description)
        thematic_tags = self.determine_thematic_tags(title, description, area)
        categories = self.determine_categories(title, description, area, thematic_tags)
        attributes = self.determine_attributes(title, description)
        difficulty = self.determine_difficulty(title, description)

        return {
            "area": area,
            "thematic_tags": thematic_tags,
            "categories": categories,
            "attributes": attributes,
            "difficulty": difficulty
        }


def tag_courses_from_json(input_file: str, output_file: str):
    """
    Читает курсы из JSON файла, тегирует их и сохраняет результат

    Args:
        input_file: путь к входному JSON файлу с курсами
        output_file: путь к выходному JSON файлу с тегами
    """
    print(f"Загрузка курсов из {input_file}...")

    # Читаем входной файл
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    courses = data.get('courses', [])
    print(f"Найдено курсов: {len(courses)}")

    # Инициализируем генератор тегов
    print("Инициализация генератора тегов...")
    generator = CourseTagGenerator()

    # Тегируем каждый курс
    tagged_courses = []
    for i, course in enumerate(courses, 1):
        course_id = course.get('id')
        name = course.get('name', '')
        description = course.get('description', '')

        print(f"\rОбработка курса {i}/{len(courses)}: {name[:50]}...", end='')

        # Генерируем теги
        tags = generator.generate_tags(name, description)

        # Добавляем теги к курсу
        tagged_course = {
            'id': course_id,
            'name': name,
            'description': description,
            'tags': tags
        }

        tagged_courses.append(tagged_course)

    print("\n\nСохранение результатов...")

    # Сохраняем результат
    output_data = {
        'courses': tagged_courses,
        'total_courses': len(tagged_courses)
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"✅ Готово! Результаты сохранены в {output_file}")

    # Выводим статистику
    print("\n" + "=" * 60)
    print("СТАТИСТИКА:")
    print("=" * 60)

    # Подсчитываем частоту областей
    area_counter = Counter()
    difficulty_counter = Counter()

    for course in tagged_courses:
        area_counter[course['tags']['area']] += 1
        difficulty_counter[course['tags']['difficulty']] += 1

    print("\nРаспределение по областям:")
    for area, count in area_counter.most_common():
        print(f"  {area}: {count} курсов")

    print("\nРаспределение по сложности:")
    for difficulty, count in difficulty_counter.most_common():
        print(f"  {difficulty}: {count} курсов")

    # Показываем примеры
    print("\n" + "=" * 60)
    print("ПРИМЕРЫ ТЕГИРОВАНИЯ (первые 5 курсов):")
    print("=" * 60)

    for course in tagged_courses[:5]:
        print(f"\n📚 {course['name']}")
        print(f"   Описание: {course['description'][:80]}...")
        print(f"   Теги:")
        for key, value in course['tags'].items():
            print(f"     {key}: {value}")


if __name__ == "__main__":
    # Пути к файлам
    input_file = "courses.json"
    output_file = "courses_tagged.json"

    # Запускаем тегирование
    tag_courses_from_json(input_file, output_file)