"""
Парсер дерева навыков из JSON файла
Загружает иерархическую структуру навыков и выводит их с подскиллами
"""

import json
from typing import Dict, Optional, List
from grades import Skill, SkillLevel


class SkillTreeParser:
    """Парсер для загрузки дерева навыков из JSON"""

    def __init__(self, json_file_path: str):
        self.json_file_path = json_file_path
        self.skills_dict: Dict[str, Skill] = {}
        self.root_skills: List[Skill] = []

    def parse(self) -> Dict[str, Skill]:
        """
        Парсить JSON файл и создать дерево навыков
        Возвращает словарь {skill_code: Skill}
        """
        print(f"📖 Загрузка навыков из {self.json_file_path}...")

        with open(self.json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        skills_tree = data.get('skills_tree', {})

        # Парсим каждую категорию верхнего уровня
        for category_key, category_data in skills_tree.items():
            root_skill = self._parse_skill_recursive(category_data, parent_skill=None)
            self.root_skills.append(root_skill)

        print(f"✅ Загружено {len(self.skills_dict)} навыков")
        print(f"📊 Корневых категорий: {len(self.root_skills)}")
        print()

        return self.skills_dict

    def _parse_skill_recursive(
            self,
            skill_data: dict,
            parent_skill: Optional[Skill]
    ) -> Skill:
        """
        Рекурсивно парсить навык и его подскиллы
        """
        # Создаём текущий навык
        skill = Skill(
            name=skill_data['name'],
            code=skill_data['code'],
            description=skill_data['description'],
            parent_skill=parent_skill,
            level=SkillLevel.LEVEL_0
        )

        # Добавляем в словарь
        self.skills_dict[skill.code] = skill

        # Обрабатываем дочерние навыки
        children_data = skill_data.get('children', {})

        for child_key, child_data in children_data.items():
            child_skill = self._parse_skill_recursive(child_data, parent_skill=skill)
            # child_skill автоматически добавится в skill.children_skills

        return skill

    def print_tree(self, max_depth: int = 3):
        """
        Вывести дерево навыков в консоль
        """
        print("=" * 80)
        print("ДЕРЕВО НАВЫКОВ")
        print("=" * 80)
        print()

        for root_skill in self.root_skills:
            self._print_skill_recursive(root_skill, depth=0, max_depth=max_depth)

        print("=" * 80)

    def _print_skill_recursive(self, skill: Skill, depth: int, max_depth: int):
        """
        Рекурсивно вывести навык и его подскиллы
        """
        if depth > max_depth:
            return

        # Создаём отступ
        indent = "  " * depth

        # Выбираем символ для дерева
        if depth == 0:
            prefix = "📁 "
        elif depth == 1:
            prefix = "├─ "
        else:
            prefix = "└─ "

        # Выводим навык
        print(f"{indent}{prefix}{skill.name}")
        print(f"{indent}   Code: {skill.code}")
        print(f"{indent}   {skill.description}")

        if skill.children_skills:
            print(f"{indent}   Подскиллов: {len(skill.children_skills)}")

        print()

        # Рекурсивно выводим дочерние навыки
        for child in skill.children_skills:
            self._print_skill_recursive(child, depth + 1, max_depth)

    def get_skills_by_category(self, category_code: str) -> List[Skill]:
        """
        Получить все навыки определённой категории
        """
        category_skills = []

        for code, skill in self.skills_dict.items():
            if code.startswith(category_code):
                category_skills.append(skill)

        return category_skills

    def print_category_summary(self):
        """
        Вывести сводку по категориям навыков
        """
        print("=" * 80)
        print("СВОДКА ПО КАТЕГОРИЯМ НАВЫКОВ")
        print("=" * 80)
        print()

        for root_skill in self.root_skills:
            # Подсчитываем количество всех подскиллов
            total_skills = self._count_all_skills(root_skill)

            print(f"📁 {root_skill.name}")
            print(f"   Code: {root_skill.code}")
            print(f"   Всего навыков в категории: {total_skills}")
            print(f"   Прямых подкатегорий: {len(root_skill.children_skills)}")

            # Выводим подкатегории уровня 2
            if root_skill.children_skills:
                print(f"   Подкатегории:")
                for child in root_skill.children_skills:
                    child_count = self._count_all_skills(child)
                    print(f"      • {child.name} ({child_count} навыков)")

            print()

        print("=" * 80)

    def _count_all_skills(self, skill: Skill) -> int:
        """
        Рекурсивно подсчитать количество всех навыков в ветке
        """
        count = 1  # Текущий навык

        for child in skill.children_skills:
            count += self._count_all_skills(child)

        return count

    def find_skill_by_name(self, name: str) -> List[Skill]:
        """
        Найти навыки по имени (поиск подстроки)
        """
        results = []
        search_lower = name.lower()

        for skill in self.skills_dict.values():
            if search_lower in skill.name.lower():
                results.append(skill)

        return results

    def get_skill_path(self, skill: Skill) -> str:
        """
        Получить полный путь навыка от корня
        """
        path_parts = []
        current = skill

        while current:
            path_parts.insert(0, current.name)
            current = current.parent_skill

        return " → ".join(path_parts)


def demo_skill_parser():
    """Демонстрация работы парсера навыков"""

    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "ДЕМОНСТРАЦИЯ ПАРСЕРА НАВЫКОВ" + " " * 30 + "║")
    print("╚" + "═" * 78 + "╝")
    print("\n")

    # Создаём парсер
    parser = SkillTreeParser('skill_tree.json')

    # Парсим файл
    skills_dict = parser.parse()

    # === 1. Вывод сводки по категориям ===
    parser.print_category_summary()

    # === 2. Вывод полного дерева (до 3 уровней) ===
    print("\n")
    print("=" * 80)
    print("ПОЛНОЕ ДЕРЕВО НАВЫКОВ (первые 3 уровня)")
    print("=" * 80)
    print()

    parser.print_tree(max_depth=2)

    # === 3. Детальный вывод конкретных категорий ===
    print("\n")
    print("=" * 80)
    print("ДЕТАЛЬНЫЙ ВЫВОД: ПРОГРАММИРОВАНИЕ")
    print("=" * 80)
    print()

    # Находим категорию программирования
    programming_skill = skills_dict.get('programming')
    if programming_skill:
        print(f"📁 {programming_skill.name}")
        print(f"   {programming_skill.description}")
        print(f"\n   Языки программирования и фреймворки:\n")

        for lang in programming_skill.children_skills:
            print(f"   ├─ {lang.name} ({lang.code})")
            print(f"   │  {lang.description}")

            if lang.children_skills:
                print(f"   │  Фреймворки и библиотеки:")
                for framework in lang.children_skills:
                    print(f"   │     • {framework.name}: {framework.description}")
            print()

    # === 4. Детальный вывод: Машинное обучение ===
    print("\n")
    print("=" * 80)
    print("ДЕТАЛЬНЫЙ ВЫВОД: МАШИННОЕ ОБУЧЕНИЕ")
    print("=" * 80)
    print()

    ml_skill = skills_dict.get('machine_learning')
    if ml_skill:
        print(f"📁 {ml_skill.name}")
        print(f"   {ml_skill.description}")
        print(f"\n   Подобласти ML:\n")

        for subarea in ml_skill.children_skills:
            print(f"   ├─ {subarea.name} ({subarea.code})")
            print(f"   │  {subarea.description}")

            if subarea.children_skills:
                print(f"   │  Инструменты и технологии:")
                for tool in subarea.children_skills:
                    print(f"   │     • {tool.name}: {tool.description}")
            print()

    # === 5. Поиск навыков ===
    print("\n")
    print("=" * 80)
    print("ПОИСК НАВЫКОВ")
    print("=" * 80)
    print()

    search_terms = ["Docker", "React", "PyTorch", "SQL"]

    for term in search_terms:  # TODO: поиск можно не только по имени и вынести в отдельную функцию
        results = parser.find_skill_by_name(term)
        print(f"🔍 Поиск: '{term}'")

        if results:
            for skill in results:
                path = parser.get_skill_path(skill)
                print(f"   ✓ Найдено: {path}")
                print(f"     Code: {skill.code}")
                print(f"     {skill.description}")
        else:
            print(f"   ✗ Не найдено")
        print()

    # === 6. Статистика ===
    print("\n")
    print("=" * 80)
    print("СТАТИСТИКА")
    print("=" * 80)
    print()

    total_skills = len(skills_dict)
    root_categories = len(parser.root_skills)

    # Подсчёт навыков по уровням
    level_counts = {1: 0, 2: 0, 3: 0}

    for skill in skills_dict.values():
        # Определяем уровень по количеству точек в коде
        level = skill.code.count('.') + 1
        if level <= 3:
            level_counts[level] = level_counts.get(level, 0) + 1

    print(f"📊 Всего навыков в дереве: {total_skills}")
    print(f"📁 Корневых категорий: {root_categories}")
    print(f"\n   Распределение по уровням:")
    print(f"      • Уровень 1 (категории): {level_counts[1]}")
    print(f"      • Уровень 2 (подкатегории): {level_counts[2]}")
    print(f"      • Уровень 3 (конкретные навыки): {level_counts[3]}")
    print()

    # Топ-5 категорий по количеству навыков
    category_sizes = []
    for root in parser.root_skills:
        count = parser._count_all_skills(root)
        category_sizes.append((root.name, count))

    category_sizes.sort(key=lambda x: x[1], reverse=True)

    print("   Топ-5 категорий по количеству навыков:")
    for i, (name, count) in enumerate(category_sizes[:5], 1):
        print(f"      {i}. {name}: {count} навыков")

    print()
    print("=" * 80)
    print()

    return parser, skills_dict


if __name__ == "__main__":
    parser, skills_dict = demo_skill_parser()

    print("\n✅ Парсинг завершён! Дерево навыков готово к использованию.\n")
