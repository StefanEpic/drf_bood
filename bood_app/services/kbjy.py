from django.db.models import Q
from rest_framework.exceptions import ValidationError

from bood_app.models import PersonCard, Measurement, ProductWeight, Product, Water, ProductCategory
import datetime


def get_ideal_weight(gender: str, hand: float, height: float) -> float:
    """
    Расчет идеального веса
    """
    ideal_weight = 0.0
    if gender == "male":
        if hand < 18:
            ideal_weight = height * 0.375
        if 18 <= hand <= 20:
            ideal_weight = height * 0.39
        if hand > 20:
            ideal_weight = height * 0.41
    if gender == "female":
        if hand < 16:
            ideal_weight = height * 0.325
        if 16 <= hand <= 17:
            ideal_weight = height * 0.34
        if hand > 17:
            ideal_weight = height * 0.355
    return ideal_weight


def get_measurements(person_card: PersonCard, date: datetime.date) -> Measurement:
    """
    Получение последних замеров пользователя
    """
    measurements = (
        Measurement.objects.filter(person_card_id=person_card.id, datetime_add__date__lte=date)
        .order_by("-datetime_add")
        .first()
    )
    if not measurements:
        raise ValidationError({"status": "400", "error": "Measurements not found"})
    return measurements


def get_one_product_by_proportion(
    proteins_proportion: float,
    fats_proportion: float,
    carbohydrates_proportion: float,
    error_value: float,
    exclude_products_ids: list,
    exclude_categories_ids: list,
) -> Product:
    """
    Найти продукт с похожей пропорцией с учетом погрешности, и с исключением определенных продуктов и категорий
    """
    product = (
        Product.objects.filter(
            Q(
                proteins_proportion__gte=proteins_proportion - error_value,
                fats_proportion__gte=fats_proportion - error_value,
                carbohydrates_proportion__gte=carbohydrates_proportion - error_value,
            )
            & Q(
                proteins_proportion__lte=proteins_proportion + error_value,
                fats_proportion__lte=fats_proportion + error_value,
                carbohydrates_proportion__lte=carbohydrates_proportion + error_value,
            )
            & Q(category__isnull=False)
        )
        .exclude(Q(id__in=exclude_products_ids) | Q(category__id__in=exclude_categories_ids))
        .first()
    )
    return product


def get_products_group_by_proportion(
    person_card: PersonCard,
    proteins_proportion: float,
    fats_proportion: float,
    carbohydrates_proportion: float,
    exclude_eaten_product_by_recommendation: Product,
) -> list:
    """
    Получить список продуктов без исключенных продуктов
    """
    result = []
    product = None
    error_value = 5
    find_product_cycle_counts = 0
    exclude_products_ids = list(Product.objects.filter(personcard=person_card).values_list("id", flat=True))
    exclude_categories_ids = list(ProductCategory.objects.filter(personcard=person_card).values_list("id", flat=True))
    # Исключение из рекомендованного списка продуктов рекомендованный к исключению продукт
    exclude_products_ids.append(exclude_eaten_product_by_recommendation.id)
    # Поиск продуктов в БД с увеличением погрешности поиска, пока не найдено 4 продукта или не выполнен лимит запросов
    while len(result) < 4:
        # Поиск продукта. Добавление категории найденного продукта в список исключаемых
        while not product and find_product_cycle_counts < 50:
            product = get_one_product_by_proportion(
                proteins_proportion,
                fats_proportion,
                carbohydrates_proportion,
                error_value,
                exclude_products_ids,
                exclude_categories_ids,
            )
            # Рост погрешности в прогрессии
            if error_value < 10:
                error_value += 5
            else:
                error_value += 20
            find_product_cycle_counts += 1

        if find_product_cycle_counts < 50:
            result.append(product)
            exclude_categories_ids.append(product.category.id)
            product = None
            error_value = 1
            find_product_cycle_counts = 0
        else:
            break
    return result


class KBJYService:
    """
    Расчет КБЖУ
    """

    def __init__(self, person_card: PersonCard, date: datetime.date):
        self.measurements = get_measurements(person_card, date)
        self.date = date
        self.id = person_card.pk
        self.gender = person_card.gender
        self.age = person_card.age
        self.weight = self.measurements.weight
        self.height = person_card.height
        self.hand = self.measurements.hand
        self.amr = float(person_card.activity)
        self.ideal_weight = get_ideal_weight(self.gender, self.hand, self.height)

    def get_imt(self) -> dict:
        """
        Расчет ИМТ
        """
        bmi = self.weight / (self.height / 100) ** 2

        imt = {}
        if self.gender == "male":
            if self.hand < 18:
                imt = ("Эктоморф", bmi)
            if 18 <= self.hand <= 20:
                imt = ("Мезоморф", bmi)
            if self.hand > 20:
                imt = ("Эндоморф", bmi)
        if self.gender == "female":
            if self.hand < 16:
                imt = ("Эктоморф", bmi)
            if 16 <= self.hand <= 17:
                imt = ("Мезоморф", bmi)
            if self.hand > 17:
                imt = ("Эндоморф", bmi)

        return {"type": imt[0], "value": round(imt[1], 1)}

    def get_standard(self) -> dict:
        """
        Расчет лимитов КБЖУ в зависимости от даты
        """
        calories = 0.0
        if self.gender == "male":
            calories = (
                ((10 * self.ideal_weight) + (6.25 * self.height) - (5 * self.age) + 5)
                + (self.ideal_weight * 24)
                + (21.3 * self.ideal_weight + 370)
                + (66.5 + 13.7 * self.ideal_weight + 5 * self.height - 6.8 * self.age)
            ) / 4
        if self.gender == "female":
            calories = (
                ((10 * self.ideal_weight) + (6.25 * self.height) - (5 * self.age) - 161)
                + (self.ideal_weight * 24)
                + (21.3 * self.ideal_weight + 370)
                + (447.6 + 9.2 * self.ideal_weight + 3.1 * self.height - 4.3 * self.age)
            ) / 4

        total_calories = (calories + (calories * 0.1)) * self.amr
        proteins = calories * 0.14 / 3.8
        fats = calories * 0.3 / 9.3
        carbohydrates = calories * 0.56 / 4.1
        water = self.weight * 30

        return {
            "calories": round(total_calories),
            "proteins": round(proteins),
            "fats": round(fats),
            "carbohydrates": round(carbohydrates),
            "water": round(water),
        }

    def get_current(self) -> dict:
        """
        Расчет текущих показателей КБЖУ в зависимости от даты
        """
        products_list = ProductWeight.objects.filter(
            Q(eating__datetime_add__date=self.date, eating__person_card_id=self.id)
            | Q(recipe__eating__datetime_add__date=self.date, recipe__eating__person_card_id=self.id)
        )
        water_list = sum(
            Water.objects.filter(eating__datetime_add__date=self.date, eating__person_card_id=self.id).values_list(
                "weight", flat=True
            )
        )

        calories = 0.0
        proteins = 0.0
        fats = 0.0
        carbohydrates = 0.0
        water = 0.0

        for prod in products_list:
            product = Product.objects.get(id=prod.product_id)
            calories += product.calories * prod.weight
            proteins += product.proteins * prod.weight
            fats += product.fats * prod.weight
            carbohydrates += product.carbohydrates * prod.weight
            water += product.water * prod.weight

        return {
            "calories": round(calories),
            "proteins": round(proteins),
            "fats": round(fats),
            "carbohydrates": round(carbohydrates),
            "water": round(water + water_list),
        }


class RecommendationService(KBJYService):
    """
    Подбор рекомендаций
    """

    def __init__(self, person_card: PersonCard, date: datetime.date):
        super().__init__(person_card, date)
        self.person_card = person_card
        self.date = date
        self.standard = self.get_standard()
        self.current = self.get_current()
        self.split_proteins = self.standard["proteins"] - self.current["proteins"]
        self.split_fats = self.standard["fats"] - self.current["fats"]
        self.split_carbohydrates = self.standard["carbohydrates"] - self.current["carbohydrates"]
        self.proportion = [self.split_proteins, self.split_fats, self.split_carbohydrates]
        self.eaten_products = Product.objects.filter(
            Q(
                product_weight__eating__datetime_add__date=self.date,
                product_weight__eating__person_card_id=self.person_card.pk,
            )
            | Q(
                product_weight__recipe__eating__datetime_add__date=self.date,
                product_weight__recipe__eating__person_card_id=self.person_card.pk,
            )
        )

    def __find_exclude_product(self) -> Product:
        """
        Поиск рекомендованного к исключению продукта
        """
        proportion = {
            "proteins": self.split_proteins,
            "fats": self.split_fats,
            "carbohydrates": self.split_carbohydrates,
        }
        max_value = sorted(proportion.items(), key=lambda item: item[1])[-1]
        result = self.eaten_products.order_by(max_value[0]).first()
        return result

    def get_include_products(self) -> list:
        """
        Получение списка рекомендованных продуктов
        """
        # Необходимо съесть минимум 3 продукта
        if len(self.eaten_products) > 2:
            exclude_product = self.__find_exclude_product()
            # БЖУ ниже нормы
            if self.split_proteins > 0 and self.split_fats > 0 and self.split_carbohydrates > 0:
                min_value = min(self.proportion)
                proteins_proportion = round(self.split_proteins / min_value, 2)
                fats_proportion = round(self.split_fats / min_value, 2)
                carbohydrates_proportion = round(self.split_carbohydrates / min_value, 2)
                return get_products_group_by_proportion(
                    self.person_card,
                    proteins_proportion,
                    fats_proportion,
                    carbohydrates_proportion,
                    exclude_product,
                )
            # БЖУ выше нормы
            if self.split_proteins < 0 and self.split_fats < 0 and self.split_carbohydrates < 0:
                max_value = max(self.proportion)
                proteins_proportion = round(max_value / self.split_proteins, 2)
                fats_proportion = round(max_value / self.split_fats, 2)
                carbohydrates_proportion = round(max_value / self.split_carbohydrates, 2)
                return get_products_group_by_proportion(
                    self.person_card,
                    proteins_proportion,
                    fats_proportion,
                    carbohydrates_proportion,
                    exclude_product,
                )
            # Б ниже нормы, ЖУ выше нормы
            if self.split_proteins > 0 and self.split_fats <= 0 and self.split_carbohydrates <= 0:
                proteins_proportion = abs(self.split_proteins)
                fats_proportion = 1
                carbohydrates_proportion = 1
                return get_products_group_by_proportion(
                    self.person_card,
                    proteins_proportion,
                    fats_proportion,
                    carbohydrates_proportion,
                    exclude_product,
                )
            # Ж ниже нормы, БУ выше нормы
            if self.split_proteins <= 0 and self.split_fats > 0 and self.split_carbohydrates <= 0:
                proteins_proportion = 1
                fats_proportion = abs(self.split_fats)
                carbohydrates_proportion = 1
                return get_products_group_by_proportion(
                    self.person_card,
                    proteins_proportion,
                    fats_proportion,
                    carbohydrates_proportion,
                    exclude_product,
                )
            # У ниже нормы, БЖ выше нормы
            if self.split_proteins <= 0 and self.split_fats <= 0 and self.split_carbohydrates > 0:
                proteins_proportion = 1
                fats_proportion = 1
                carbohydrates_proportion = abs(self.split_carbohydrates)
                return get_products_group_by_proportion(
                    self.person_card,
                    proteins_proportion,
                    fats_proportion,
                    carbohydrates_proportion,
                    exclude_product,
                )
            # БЖ ниже нормы, У выше нормы
            if self.split_proteins > 0 and self.split_fats > 0 and self.split_carbohydrates <= 0:
                proteins_proportion = abs(self.split_proteins)
                fats_proportion = abs(self.split_fats)
                carbohydrates_proportion = 1
                return get_products_group_by_proportion(
                    self.person_card,
                    proteins_proportion,
                    fats_proportion,
                    carbohydrates_proportion,
                    exclude_product,
                )
            # ЖУ ниже нормы, Б выше нормы
            if self.split_proteins <= 0 and self.split_fats > 0 and self.split_carbohydrates > 0:
                proteins_proportion = 1
                fats_proportion = abs(self.split_fats)
                carbohydrates_proportion = abs(self.split_carbohydrates)
                return get_products_group_by_proportion(
                    self.person_card,
                    proteins_proportion,
                    fats_proportion,
                    carbohydrates_proportion,
                    exclude_product,
                )
            # БУ ниже нормы, Ж выше нормы
            if self.split_proteins > 0 and self.split_fats <= 0 and self.split_carbohydrates > 0:
                proteins_proportion = abs(self.split_proteins)
                fats_proportion = 1
                carbohydrates_proportion = abs(self.split_carbohydrates)
                return get_products_group_by_proportion(
                    self.person_card,
                    proteins_proportion,
                    fats_proportion,
                    carbohydrates_proportion,
                    exclude_product,
                )
        else:
            raise ValidationError({"status": "400", "error": "There are too low eating to make recommendations"})

    def get_exclude_product(self) -> Product:
        """
        Получение рекомендованного к исключению продукта
        """
        # Необходимо съесть минимум 3 продукта
        if len(self.eaten_products) > 2:
            return self.__find_exclude_product()
        else:
            raise ValidationError({"status": "400", "error": "There are too low eating to make recommendations"})
