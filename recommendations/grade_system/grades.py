"""
Динамический планировщик образовательной траектории
Система управления компетенциями студентов с иерархической структурой навыков
"""

from enum import Enum
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json


class SkillLevel(Enum):
    """10-уровневая система оценки навыков (как в CodeWars)"""
    LEVEL_0 = 0  # Нет опыта
    LEVEL_1 = 1  # Новичок (Beginner)
    LEVEL_2 = 2  # Базовый (Elementary)
    LEVEL_3 = 3  # Начальный (Pre-Intermediate)
    LEVEL_4 = 4  # Средний-начальный (Intermediate)
    LEVEL_5 = 5  # Средний (Upper-Intermediate)
    LEVEL_6 = 6  # Продвинутый-начальный (Advanced)
    LEVEL_7 = 7  # Продвинутый (Proficient)
    LEVEL_8 = 8  # Мастер (Expert)
    LEVEL_9 = 9  # Гуру (Master)
    LEVEL_10 = 10  # Легенда (Grandmaster)


class CourseDifficulty(Enum):
    """Уровни сложности курсов"""
    BEGINNER = "Начальный"
    INTERMEDIATE = "Продвинутый"
    ADVANCED = "Экспертный"


@dataclass
class Skill:
    """
    Иерархический навык с возможностью вложенности
    Например: Python -> Django -> REST API
    """
    name: str
    code: str  # Уникальный код навыка (например: "python.django.rest")
    description: str
    parent_skill: Optional['Skill'] = None
    children_skills: List['Skill'] = field(default_factory=list)
    level: SkillLevel = SkillLevel.LEVEL_0

    def __post_init__(self):
        if self.parent_skill:
            if self not in self.parent_skill.children_skills:
                self.parent_skill.children_skills.append(self)

    def get_full_path(self) -> str:
        """Получить полный путь навыка"""
        if self.parent_skill:
            return f"{self.parent_skill.get_full_path()}.{self.name}"
        return self.name

    def is_child_of(self, skill: 'Skill') -> bool:
        """Проверить, является ли текущий навык подкомпетенцией другого навыка"""
        current = self.parent_skill
        while current:
            if current == skill:
                return True
            current = current.parent_skill
        return False

    def __repr__(self):
        return f"Skill({self.name}, level={self.level.value})"


@dataclass
class SkillRequirement:
    """Требование к навыку для курса или специальности"""
    skill: Skill
    required_level: SkillLevel
    weight: float = 1.0  # Вес навыка (важность от 0 до 1)

    def is_satisfied(self, student_level: SkillLevel) -> bool:
        """Проверить, удовлетворяет ли уровень студента требованию"""
        return student_level.value >= self.required_level.value


@dataclass
class SkillGain:
    """Приращение навыка от курса"""
    skill: Skill
    base_gain: int  # Базовое приращение уровня
    max_level: SkillLevel  # Максимальный уровень, которого можно достичь

    def calculate_gain(self, current_level: SkillLevel, performance: float) -> int:
        """
        Рассчитать реальное приращение с учётом текущего уровня и успеваемости
        performance: оценка за курс (0.0 - 1.0)
        """
        if current_level.value >= self.max_level.value:
            return 0

        # Приращение зависит от успеваемости
        actual_gain = int(self.base_gain * performance)

        # Не превышаем максимальный уровень
        new_level = min(current_level.value + actual_gain, self.max_level.value)
        return new_level - current_level.value


@dataclass
class Course:
    """Адаптивный курс"""
    code: str  # Уникальный код курса
    name: str
    description: str
    is_elective: bool  # Элективный или обязательный
    semester: int  # Рекомендуемый семестр
    credits: int  # Кредиты ECTS

    # Требования для записи на курс
    prerequisites: List[SkillRequirement] = field(default_factory=list)

    # Навыки, которые развивает курс (зависит от сложности)
    skill_gains: Dict[CourseDifficulty, List[SkillGain]] = field(default_factory=dict)

    # Адаптивная сложность
    adaptive: bool = True

    def get_difficulty_for_student(self, student_skills: Dict[str, SkillLevel]) -> CourseDifficulty:
        """
        Определить подходящую сложность курса для студента
        на основе его текущих навыков
        """
        if not self.adaptive:
            return CourseDifficulty.INTERMEDIATE

        # Проверяем уровень подготовки по пререквизитам
        total_score = 0
        max_score = 0

        for req in self.prerequisites:
            skill_code = req.skill.code
            student_level = student_skills.get(skill_code, SkillLevel.LEVEL_0)
            total_score += student_level.value
            max_score += req.required_level.value

        if max_score == 0:
            return CourseDifficulty.BEGINNER

        ratio = total_score / max_score

        if ratio < 0.7:
            return CourseDifficulty.BEGINNER
        elif ratio < 1.3:
            return CourseDifficulty.INTERMEDIATE
        else:
            return CourseDifficulty.ADVANCED

    def get_skill_gains_for_difficulty(self, difficulty: CourseDifficulty) -> List[SkillGain]:
        """Получить набор навыков для конкретной сложности"""
        return self.skill_gains.get(difficulty, [])

    def __repr__(self):
        return f"Course({self.code}: {self.name})"


@dataclass
class CourseCompletion:
    """Запись о пройденном курсе"""
    course: Course
    grade: float  # Оценка от 0 до 100
    difficulty: CourseDifficulty  # Фактическая сложность прохождения
    completion_date: datetime
    semester: int

    def get_performance(self) -> float:
        """Преобразовать оценку в коэффициент успеваемости (0.0 - 1.0)"""
        return min(self.grade / 100.0, 1.0)

    def get_normalized_grade(self) -> str:
        """Получить буквенную оценку"""
        if self.grade >= 90:
            return "A"
        elif self.grade >= 80:
            return "B"
        elif self.grade >= 70:
            return "C"
        elif self.grade >= 60:
            return "D"
        else:
            return "F"


@dataclass
class MasterProgram:
    """Направление магистратуры"""
    code: str  # Например: "09.04.01"
    name: str
    description: str

    # Обязательные курсы
    required_courses: List[Course] = field(default_factory=list)

    # Элективные курсы (студент выбирает из них)
    elective_courses: List[Course] = field(default_factory=list)

    # Целевые компетенции для выпуска
    target_skills: List[SkillRequirement] = field(default_factory=list)

    # Минимальное количество элективных курсов
    min_electives: int = 5

    # Общая продолжительность (семестров)
    duration_semesters: int = 4

    def get_all_courses(self) -> List[Course]:
        """Получить все курсы программы"""
        return self.required_courses + self.elective_courses

    def get_courses_for_semester(self, semester: int) -> Tuple[List[Course], List[Course]]:
        """Получить обязательные и элективные курсы для семестра"""
        required = [c for c in self.required_courses if c.semester == semester]
        elective = [c for c in self.elective_courses if c.semester == semester]
        return required, elective

    def check_graduation_requirements(self, student_skills: Dict[str, SkillLevel]) -> Tuple[
        bool, List[SkillRequirement]]:
        """
        Проверить, соответствует ли студент требованиям выпуска
        Возвращает: (готов_к_выпуску, список_недостающих_компетенций)
        """
        missing_skills = []

        for req in self.target_skills:
            skill_code = req.skill.code
            student_level = student_skills.get(skill_code, SkillLevel.LEVEL_0)

            if not req.is_satisfied(student_level):
                missing_skills.append(req)

        return len(missing_skills) == 0, missing_skills


class Student:
    """Студент с персонализированной траекторией обучения"""

    def __init__(
            self,
            student_id: str,
            name: str,
            program: MasterProgram,
            current_semester: int = 1
    ):
        self.student_id = student_id
        self.name = name
        self.program = program
        self.current_semester = current_semester

        # Текущие навыки студента {skill_code: SkillLevel}
        self.skills: Dict[str, SkillLevel] = {}

        # Пройденные курсы
        self.completed_courses: List[CourseCompletion] = []

        # Курсы в текущем семестре
        self.enrolled_courses: List[Course] = []

    def get_skill_level(self, skill_code: str) -> SkillLevel:
        """Получить уровень навыка"""
        return self.skills.get(skill_code, SkillLevel.LEVEL_0)

    def update_skill(self, skill_code: str, new_level: SkillLevel):
        """Обновить уровень навыка"""
        current_level = self.get_skill_level(skill_code)
        if new_level.value > current_level.value:
            self.skills[skill_code] = new_level

    def complete_course(
            self,
            course: Course,
            grade: float,
            semester: int,
            completion_date: Optional[datetime] = None
    ):
        """
        Завершить курс и обновить навыки
        """
        if completion_date is None:
            completion_date = datetime.now()

        # Определяем сложность, с которой студент прошёл курс
        difficulty = course.get_difficulty_for_student(self.skills)

        # Записываем завершение курса
        completion = CourseCompletion(
            course=course,
            grade=grade,
            difficulty=difficulty,
            completion_date=completion_date,
            semester=semester
        )
        self.completed_courses.append(completion)

        # Обновляем навыки
        performance = completion.get_performance()
        skill_gains = course.get_skill_gains_for_difficulty(difficulty)

        for gain in skill_gains:
            current_level = self.get_skill_level(gain.skill.code)
            level_increase = gain.calculate_gain(current_level, performance)

            if level_increase > 0:
                new_level_value = current_level.value + level_increase
                new_level = SkillLevel(new_level_value)
                self.update_skill(gain.skill.code, new_level)

    def enroll_in_course(self, course: Course) -> bool:
        """
        Записаться на курс (проверка пререквизитов)
        """
        # Проверяем, не пройден ли уже курс
        if course in [c.course for c in self.completed_courses]:
            return False

        # Проверяем пререквизиты
        for req in course.prerequisites:
            if not req.is_satisfied(self.get_skill_level(req.skill.code)):
                return False

        self.enrolled_courses.append(course)
        return True

    def get_skill_profile(self) -> Dict[str, int]:
        """Получить профиль навыков в виде словаря"""
        return {code: level.value for code, level in self.skills.items()}

    def get_graduation_readiness(self) -> Tuple[float, List[SkillRequirement]]:
        """
        Проверить готовность к выпуску
        Возвращает: (процент_готовности, недостающие_компетенции)
        """
        ready, missing = self.program.check_graduation_requirements(self.skills)

        if ready:
            return 100.0, []

        total_requirements = len(self.program.target_skills)
        satisfied_requirements = total_requirements - len(missing)
        percentage = (satisfied_requirements / total_requirements) * 100

        return percentage, missing

    def recommend_courses(self, semester: int, max_recommendations: int = 5) -> List[Tuple[Course, float]]:
        """
        Рекомендовать курсы для заданного семестра
        Возвращает: список (курс, релевантность) отсортированный по убыванию релевантности
        """
        _, missing_skills = self.get_graduation_readiness()

        # Получаем доступные курсы
        required, elective = self.program.get_courses_for_semester(semester)
        available_courses = required + elective

        # Фильтруем уже пройденные
        completed_codes = {c.course.code for c in self.completed_courses}
        available_courses = [c for c in available_courses if c.code not in completed_codes]

        recommendations = []

        for course in available_courses:
            # Проверяем доступность (пререквизиты)
            can_enroll = all(
                req.is_satisfied(self.get_skill_level(req.skill.code))
                for req in course.prerequisites
            )

            if not can_enroll:
                continue

            # Рассчитываем релевантность на основе недостающих навыков
            relevance = self._calculate_course_relevance(course, missing_skills)
            recommendations.append((course, relevance))

        # Сортируем по релевантности
        recommendations.sort(key=lambda x: x[1], reverse=True)

        return recommendations[:max_recommendations]

    def _calculate_course_relevance(
            self,
            course: Course,
            missing_skills: List[SkillRequirement]
    ) -> float:
        """Рассчитать релевантность курса для восполнения недостающих навыков"""
        if not missing_skills:
            return 0.5  # Базовая релевантность если все навыки есть

        # Получаем навыки, которые даёт курс
        difficulty = course.get_difficulty_for_student(self.skills)
        skill_gains = course.get_skill_gains_for_difficulty(difficulty)

        relevance_score = 0.0
        missing_skill_codes = {req.skill.code for req in missing_skills}

        for gain in skill_gains:
            if gain.skill.code in missing_skill_codes:
                # Находим требование для этого навыка
                requirement = next(
                    (req for req in missing_skills if req.skill.code == gain.skill.code),
                    None
                )

                if requirement:
                    # Вес зависит от важности навыка и потенциального приращения
                    current_level = self.get_skill_level(gain.skill.code)
                    potential_gain = min(
                        gain.max_level.value - current_level.value,
                        gain.base_gain
                    )
                    relevance_score += requirement.weight * potential_gain

        return relevance_score

    def simulate_alternative_program(
            self,
            alternative_program: MasterProgram
    ) -> Tuple[float, List[SkillRequirement]]:
        """
        Функция "Что, если?"
        Моделирование готовности к выпуску при выборе другой специальности
        """
        ready, missing = alternative_program.check_graduation_requirements(self.skills)

        if ready:
            return 100.0, []

        total_requirements = len(alternative_program.target_skills)
        satisfied_requirements = total_requirements - len(missing)
        percentage = (satisfied_requirements / total_requirements) * 100

        return percentage, missing

    def get_summary(self) -> Dict:
        """Получить сводную информацию о студенте"""
        readiness, missing = self.get_graduation_readiness()

        return {
            "student_id": self.student_id,
            "name": self.name,
            "program": self.program.code,
            "current_semester": self.current_semester,
            "completed_courses": len(self.completed_courses),
            "total_credits": sum(c.course.credits for c in self.completed_courses),
            "average_grade": sum(c.grade for c in self.completed_courses) / len(
                self.completed_courses) if self.completed_courses else 0,
            "skills_count": len(self.skills),
            "graduation_readiness": f"{readiness:.1f}%",
            "missing_skills_count": len(missing)
        }

    def __repr__(self):
        return f"Student({self.name}, {self.program.code}, sem={self.current_semester})"


def create_skill_tree() -> Dict[str, Skill]:
    """
    Создать иерархическое дерево навыков для IT-специальностей
    Возвращает словарь {skill_code: Skill}
    """
    skills = {}

    # === ПРОГРАММИРОВАНИЕ ===
    programming = Skill("Programming", "programming", "Программирование")
    skills["programming"] = programming

    # Python и его экосистема
    python = Skill("Python", "python", "Язык программирования Python", parent_skill=programming)
    skills["python"] = python

    django = Skill("Django", "python.django", "Веб-фреймворк Django", parent_skill=python)
    skills["python.django"] = django

    flask = Skill("Flask", "python.flask", "Микрофреймворк Flask", parent_skill=python)
    skills["python.flask"] = flask

    pandas = Skill("Pandas", "python.pandas", "Библиотека анализа данных", parent_skill=python)
    skills["python.pandas"] = pandas

    numpy = Skill("NumPy", "python.numpy", "Библиотека для численных вычислений", parent_skill=python)
    skills["python.numpy"] = numpy

    # JavaScript и frontend
    javascript = Skill("JavaScript", "javascript", "Язык JavaScript", parent_skill=programming)
    skills["javascript"] = javascript

    react = Skill("React", "javascript.react", "Библиотека React", parent_skill=javascript)
    skills["javascript.react"] = react

    vue = Skill("Vue.js", "javascript.vue", "Фреймворк Vue.js", parent_skill=javascript)
    skills["javascript.vue"] = vue

    nodejs = Skill("Node.js", "javascript.nodejs", "Серверная платформа Node.js", parent_skill=javascript)
    skills["javascript.nodejs"] = nodejs

    # Java
    java = Skill("Java", "java", "Язык программирования Java", parent_skill=programming)
    skills["java"] = java

    spring = Skill("Spring", "java.spring", "Фреймворк Spring", parent_skill=java)
    skills["java.spring"] = spring

    # C++ и системное программирование
    cpp = Skill("C++", "cpp", "Язык программирования C++", parent_skill=programming)
    skills["cpp"] = cpp

    # === БАЗЫ ДАННЫХ ===
    databases = Skill("Databases", "databases", "Базы данных")
    skills["databases"] = databases

    sql = Skill("SQL", "databases.sql", "Язык запросов SQL", parent_skill=databases)
    skills["databases.sql"] = sql

    postgresql = Skill("PostgreSQL", "databases.postgresql", "СУБД PostgreSQL", parent_skill=databases)
    skills["databases.postgresql"] = postgresql

    mongodb = Skill("MongoDB", "databases.mongodb", "NoSQL база MongoDB", parent_skill=databases)
    skills["databases.mongodb"] = mongodb

    redis = Skill("Redis", "databases.redis", "In-memory БД Redis", parent_skill=databases)
    skills["databases.redis"] = redis

    # === МАШИННОЕ ОБУЧЕНИЕ ===
    ml = Skill("Machine Learning", "ml", "Машинное обучение")
    skills["ml"] = ml

    sklearn = Skill("Scikit-learn", "ml.sklearn", "Библиотека scikit-learn", parent_skill=ml)
    skills["ml.sklearn"] = sklearn

    tensorflow = Skill("TensorFlow", "ml.tensorflow", "Фреймворк TensorFlow", parent_skill=ml)
    skills["ml.tensorflow"] = tensorflow

    pytorch = Skill("PyTorch", "ml.pytorch", "Фреймворк PyTorch", parent_skill=ml)
    skills["ml.pytorch"] = pytorch

    nlp = Skill("NLP", "ml.nlp", "Обработка естественного языка", parent_skill=ml)
    skills["ml.nlp"] = nlp

    cv = Skill("Computer Vision", "ml.cv", "Компьютерное зрение", parent_skill=ml)
    skills["ml.cv"] = cv

    # === DEVOPS ===
    devops = Skill("DevOps", "devops", "DevOps практики")
    skills["devops"] = devops

    docker = Skill("Docker", "devops.docker", "Контейнеризация Docker", parent_skill=devops)
    skills["devops.docker"] = docker

    kubernetes = Skill("Kubernetes", "devops.kubernetes", "Оркестрация Kubernetes", parent_skill=devops)
    skills["devops.kubernetes"] = kubernetes

    ci_cd = Skill("CI/CD", "devops.cicd", "Непрерывная интеграция", parent_skill=devops)
    skills["devops.cicd"] = ci_cd

    # === АРХИТЕКТУРА ===
    architecture = Skill("Software Architecture", "architecture", "Архитектура ПО")
    skills["architecture"] = architecture

    microservices = Skill("Microservices", "architecture.microservices", "Микросервисная архитектура",
                          parent_skill=architecture)
    skills["architecture.microservices"] = microservices

    api_design = Skill("API Design", "architecture.api", "Проектирование API", parent_skill=architecture)
    skills["architecture.api"] = api_design

    design_patterns = Skill("Design Patterns", "architecture.patterns", "Паттерны проектирования",
                            parent_skill=architecture)
    skills["architecture.patterns"] = design_patterns

    # === АНАЛИЗ ДАННЫХ ===
    data_analysis = Skill("Data Analysis", "data_analysis", "Анализ данных")
    skills["data_analysis"] = data_analysis

    statistics = Skill("Statistics", "data_analysis.statistics", "Статистика", parent_skill=data_analysis)
    skills["data_analysis.statistics"] = statistics

    visualization = Skill("Data Visualization", "data_analysis.visualization", "Визуализация данных",
                          parent_skill=data_analysis)
    skills["data_analysis.visualization"] = visualization

    # === БЕЗОПАСНОСТЬ ===
    security = Skill("Cybersecurity", "security", "Кибербезопасность")
    skills["security"] = security

    web_security = Skill("Web Security", "security.web", "Веб-безопасность", parent_skill=security)
    skills["security.web"] = web_security

    cryptography = Skill("Cryptography", "security.crypto", "Криптография", parent_skill=security)
    skills["security.crypto"] = cryptography

    # === SOFT SKILLS ===
    soft_skills = Skill("Soft Skills", "soft", "Мягкие навыки")
    skills["soft"] = soft_skills

    teamwork = Skill("Teamwork", "soft.teamwork", "Командная работа", parent_skill=soft_skills)
    skills["soft.teamwork"] = teamwork

    communication = Skill("Communication", "soft.communication", "Коммуникация", parent_skill=soft_skills)
    skills["soft.communication"] = communication

    project_management = Skill("Project Management", "soft.pm", "Управление проектами", parent_skill=soft_skills)
    skills["soft.pm"] = project_management

    return skills


# Экспорт основных классов
__all__ = [
    'Skill',
    'SkillLevel',
    'SkillRequirement',
    'SkillGain',
    'Course',
    'CourseDifficulty',
    'CourseCompletion',
    'MasterProgram',
    'Student',
    'create_skill_tree'
]
