from django.db.models import Q
from rest_framework.exceptions import ValidationError

from bood_app.models import PersonCard, Measurement, ProductWeight, Product, Water
import datetime


def get_ideal_weight(gender: str, hand: float, height: float) -> float:
    """
    Расчет идеального веса.
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
    Получение последних замеров пользователя.
    """
    measurements = (
        Measurement.objects.filter(person_card_id=person_card.id, datetime_add__date__lte=date)
        .order_by("-datetime_add")
        .first()
    )
    if not measurements:
        raise ValidationError({"status": "400", "error": "Measurements not found"})
    return measurements


class CalculateService:
    """
    Расчет КБЖУ.
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
        bmi_index = round(self.weight / (self.height / 100) ** 2, 1)
        imt_type = ""
        if self.gender == "male":
            if self.hand < 18:
                imt_type = "Эктоморф"
            if 18 <= self.hand <= 20:
                imt_type = "Мезоморф"
            if self.hand > 20:
                imt_type = "Эндоморф"
        if self.gender == "female":
            if self.hand < 16:
                imt_type = "Эктоморф"
            if 16 <= self.hand <= 17:
                imt_type = "Мезоморф"
            if self.hand > 17:
                imt_type = "Эндоморф"
        return {"type": imt_type, "value": bmi_index}

    def get_standard(self) -> dict:
        """
        Расчет лимитов КБЖУ в зависимости от даты.
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
        Расчет текущих показателей КБЖУ в зависимости от даты.
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
