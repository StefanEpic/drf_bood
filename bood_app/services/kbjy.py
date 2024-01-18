from django.db.models import Q
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from bood_app.models import PersonCard, Measurement, ProductWeight, Product, Water
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
    try:
        measurements = Measurement.objects.filter(person_card_id=person_card.pk, datetime_add__date__lte=date).order_by(
            "-datetime_add"
        )[0]
        return measurements
    except IndexError:
        raise ValidationError({"status": "400", "error": "Measurements not found"})


class KBJYService:
    """
    Расчет КБЖУ
    """

    def __init__(self, person_card: PersonCard, date: datetime.date = timezone.now().date()):
        measurements = get_measurements(person_card, date)
        self.date = date
        self.id = person_card.pk
        self.gender = person_card.gender
        self.age = person_card.age
        self.weight = measurements.weight
        self.height = person_card.height
        self.hand = measurements.hand
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
        water_list = sum(Water.objects.filter(
            eating__datetime_add__date=self.date,
            eating__person_card_id=self.id).values_list("weight", flat=True)
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


class RecommendationService:
    """
    Подбор рекомендаций
    """

    def __init__(self, person_card: PersonCard, date: datetime.date = timezone.now().date()):
        self.person_card = person_card
        kbjy_service = KBJYService(self.person_card)
        standard = kbjy_service.get_standard()
        current = kbjy_service.get_current()
        self.standard_proteins = standard["proteins"]
        self.standard_fats = standard["fats"]
        self.standard_carbohydrates = standard["carbohydrates"]
        self.current_proteins = current["proteins"]
        self.current_fats = current["fats"]
        self.current_carbohydrates = current["carbohydrates"]
        self.date = date
        self.eaten_products = Product.objects.filter(
            Q(
                product_weight__eating__datetime_add__date=self.date,
                product_weight__eating__person_card_id=person_card.id,
            )
            | Q(
                product_weight__recipe__eating__datetime_add__date=self.date,
                product_weight__recipe__eating__person_card_id=person_card.id,
            )
        )

    def get_recommendation(self) -> dict:
        """
        Получение списка рекомендованных продуктов
        """
        if len(self.eaten_products) > 2:
            if (
                    self.current_proteins < self.standard_proteins
                    and self.current_fats < self.standard_fats
                    and self.current_carbohydrates < self.standard_carbohydrates
            ):
                proteins = self.standard_proteins - self.current_proteins
                fats = self.standard_fats - self.current_fats
                carbohydrates = self.standard_carbohydrates - self.current_carbohydrates
                proportion = [proteins, fats, carbohydrates]
                min_value = min(proportion)
                proteins_proportion = round(proteins / min_value, 2)
                fats_proportion = round(fats / min_value, 2)
                carbohydrates_proportion = round(carbohydrates / min_value, 2)

                exclude_products_ids = Product.objects.filter(
                    Q(personcard=self.person_card) | Q(category__personcard=self.person_card) | Q(category__isnull=True)
                ).values_list("id", flat=True)

                result = []
                error_value = 0.1
                end_cycle = 0
                while len(result) < 4 and end_cycle < 100:
                    result = Product.objects.filter(
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
                    ).exclude(id__in=exclude_products_ids)[:4]
                    error_value += 0.1
                    end_cycle += 1
                return {"include": result}
            if (
                    self.current_proteins > self.standard_proteins
                    or self.current_fats > self.standard_fats
                    or self.current_carbohydrates > self.standard_carbohydrates
            ):
                proteins = self.current_proteins - self.standard_proteins
                fats = self.current_fats - self.standard_fats
                carbohydrates = self.current_carbohydrates - self.standard_carbohydrates
                proportion = {"proteins": proteins, "fats": fats, "carbohydrates": carbohydrates}
                max_value = sorted(proportion.items(), key=lambda item: item[1])[-1]
                result = [self.eaten_products.order_by(max_value[0]).last()]
                return {"exclude": result}
        else:
            raise ValidationError({"status": "400", "error": "There are too low eating to make recommendations"})
