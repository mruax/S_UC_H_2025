from sentence_transformers import SentenceTransformer, util

# Загружаем модель для эмбеддингов
model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

# Список компетенций и тегов
TAGS = {
    "Программирование": "Алгоритмы, код, разработка, языки программирования",
    "Python": "pandas numpy python flask django",
    "SQL": "базы данных sql запросы postgres mysql",
    "Машинное обучение": "machine learning нейросети классификация регрессия",
    "Статистика": "математика распределения вероятность статистика",
    "Анализ данных": "data analysis визуализация аналитика dashboards",
    "Soft Skills": "коммуникации презентации навыки общения",
    "Управление проектами": "agile scrum управление проектами kanban",
    "Дизайн": "figma дизайн ui ux",
    "Маркетинг": "реклама seo брендинг маркетинг"
}

# Преобразуем описание тегов → эмбеддинги
tag_embeddings = model.encode(list(TAGS.values()), convert_to_tensor=True)
tag_names = list(TAGS.keys())


def generate_tags_embeddings(title: str, description: str, top_k=3):
    # Объединяем текст
    query = title + ". " + description

    # Эмбеддинг текста курса
    query_emb = model.encode(query, convert_to_tensor=True)

    # Считаем косинусную близость
    scores = util.pytorch_cos_sim(query_emb, tag_embeddings)[0]

    # Выбираем top-k тегов
    top_results = scores.topk(top_k)

    recommended_tags = [tag_names[idx] for idx in top_results.indices]
    return recommended_tags


# ---- пример использования ----
title = "Основы анализа данных и Python"
description = "Изучение методов анализа, визуализации данных и работы с библиотеками Python."

print(generate_tags_embeddings(title, description))
