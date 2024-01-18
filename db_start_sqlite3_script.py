import json
import sqlite3

with open("product_db.json", encoding="utf-8") as f:
    data = json.load(f)

conn = sqlite3.connect("db.sqlite3")
cursor = conn.cursor()

categoryrecommendation = [
    "Мясо и мясные продукты",
    "Птица и продукты из птицы",
    "Рыба и морепродукты",
    "Яйца",
    "Молоко и молочные продукты",
    "Хлеб и хлебобулочные изделия",
    "Крупы, макаронные изделия",
    "Бобовые",
    "Овощи",
    "Фрукты и ягоды",
    "Орехи и сухофрукты",
]

for category in categoryrecommendation:
    cursor.execute(
        """ INSERT INTO bood_app_productcategory (title, description, image) VALUES (?, ?, ?) """,
        (category, "", ""),
    )

count = 0
for product in data:
    vitamins = data[product]["Витамины"]
    try:
        a = vitamins.get("Витамин А, РЭ", 0.0)
        b1 = vitamins.get("Витамин В1, тиамин", 0.0)
        b2 = vitamins.get("Витамин В2, рибофлавин", 0.0)
        b3 = vitamins.get("Витамин РР, НЭ", 0.0)
        e = vitamins.get("Витамин Е, альфа токоферол, ТЭ", 0.0)
        c = vitamins.get("Витамин C, аскорбиновая", 0.0)

        cursor.execute(
            """ INSERT INTO bood_app_vitamin (a, b1, b2, b3, e, c) VALUES (?, ?, ?, ?, ?, ?) """, (a, b1, b2, b3, e, c)
        )
    except Exception as e:
        print(e)

    micro = data[product]["Микроэлементы"]
    try:
        iron = micro.get("Железо, Fe", 0.0)
        calcium = micro.get("Кальций, Ca", 0.0)
        sodium = micro.get("Натрий, Na", 0.0)
        potassium = micro.get("Калий, K", 0.0)
        phosphorus = micro.get("Фосфор, P", 0.0)

        cursor.execute(
            """ INSERT INTO bood_app_microelement (iron, calcium, sodium, potassium, phosphorus) VALUES (?, ?, ?, ?, ?) """,
            (iron, calcium, sodium, potassium, phosphorus),
        )
    except Exception as e:
        print(e)

    base = data[product]["КБЖУ+Вода"]
    base_proportion = data[product]["БЖУ"]
    category = data[product]["Категория"]
    if category:
        category = categoryrecommendation.index(category) + 1

    count += 1
    try:
        title = product
        proteins = base.get("Белки", 0.0)
        fats = base.get("Жиры", 0.0)
        carbohydrates = base.get("Углеводы", 0.0)
        calories = base.get("Калорийность", 0.0)
        water = base.get("Вода", 0.0)
        proteins_proportion = base_proportion.get("Б", 0.0)
        fats_proportion = base_proportion.get("Ж", 0.0)
        carbohydrates_proportion = base_proportion.get("У", 0.0)
        vitamins = str(count)
        microelements = str(count)
        category = category

        cursor.execute(
            """ INSERT INTO bood_app_product (title, proteins, fats, carbohydrates, calories, water, proteins_proportion, fats_proportion, carbohydrates_proportion, vitamins_id, microelements_id, category_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) """,
            (
                title,
                proteins,
                fats,
                carbohydrates,
                calories,
                water,
                proteins_proportion,
                fats_proportion,
                carbohydrates_proportion,
                vitamins,
                microelements,
                category,
            ),
        )
    except Exception as e:
        print(e)

conn.commit()
conn.close()
