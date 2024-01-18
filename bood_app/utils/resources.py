"""
Models resources file
"""

# PersonCard resources

GENDER_TYPE = [
    ("male", "Мужчина"),
    ("female", "Женщина"),
]

TARGET_TYPE = {
    ("gain", "Набор веса"),
    ("keep", "Поддержание формы"),
    ("lose", "Похудение"),
}

ACTIVITY_TYPE = (
    ("1.2", "Сидячий или лежачий"),
    ("1.375", "Умственный труд"),
    ("1.55", "Лёгкий физический труд (активная работа «на ногах» или тренировки 2-3 в неделю)"),
    ("1.7", "Физический труд средней тяжести (ежедневные тренировки)"),
    ("1.9", "Тяжелый физический труд (профессиональные спортсмены)"),
)