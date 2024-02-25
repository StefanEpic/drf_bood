from datetime import datetime

from django.db.models import F, Q
from django.db.models.functions import Abs
from rest_framework.exceptions import ValidationError

from bood_app.models import PersonCard, Product, ProductCategory
from bood_app.services.calculate import CalculateService


class RecommendationService(CalculateService):
    """
    Подбор рекомендаций.
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
        self.split_proportion = [self.split_proteins, self.split_fats, self.split_carbohydrates]
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

    @staticmethod
    def __get_nutrient_proportion_dict(
        proteins_proportion: float, fats_proportion: float, carbohydrates_proportion: float
    ) -> dict:
        return {
            "proteins_proportion": proteins_proportion,
            "fats_proportion": fats_proportion,
            "carbohydrates_proportion": carbohydrates_proportion,
        }

    def __find_exclude_product(self) -> Product:
        """
        Поиск рекомендованного к исключению продукта.
        """
        proportion = {
            "proteins": self.split_proteins,
            "fats": self.split_fats,
            "carbohydrates": self.split_carbohydrates,
        }
        max_value = sorted(proportion.items(), key=lambda item: item[1])[-1]
        result = self.eaten_products.order_by(max_value[0]).first()
        return result

    def __get_products_group_by_proportion(self, nutrient_dict: dict) -> list:
        """
        Получить список продуктов наиболее соответствующих пропорциям.
        """
        nutrient_list = sorted(nutrient_dict.items(), key=lambda item: item[1], reverse=True)
        exclude_products_ids = list(Product.objects.filter(personcard=self.person_card).values_list("id", flat=True))
        exclude_categories_ids = list(
            ProductCategory.objects.filter(personcard=self.person_card).values_list("id", flat=True)
        )

        # Исключение из списка продуктов рекомендованный к исключению продукт
        exclude_eaten_product_by_recommendation = self.__find_exclude_product()
        exclude_products_ids.append(exclude_eaten_product_by_recommendation.id)

        # Получаем список продуктов наиболее близких по пропорциям nutrient_list
        first_abs = Abs(F(nutrient_list[0][0]) - nutrient_list[0][1])
        second_abs = Abs(F(nutrient_list[1][0]) - nutrient_list[1][1])
        first_query = (
            Product.objects.annotate(first_abs=first_abs)
            .filter(category__isnull=False)
            .exclude(Q(id__in=exclude_products_ids) | Q(category__id__in=exclude_categories_ids))
            .order_by("first_abs")
            .values("id")[:30]
        )
        second_query = Product.objects.annotate(second_abs=second_abs).filter(pk__in=first_query).order_by("second_abs")

        # Получаем 4 наиболее подходящих продукта с разными категориями
        list_of_uniques_categories = []
        result = []
        for i in second_query:
            if i.category not in list_of_uniques_categories and len(result) < 4:
                result.append(i)
            list_of_uniques_categories.append(i.category)
        return result

    def get_include_products(self) -> list:
        """
        Получение списка рекомендованных продуктов.
        """
        # Необходимо съесть минимум 3 продукта
        if len(self.eaten_products) > 2:
            # БЖУ ниже нормы
            if self.split_proteins > 0 and self.split_fats > 0 and self.split_carbohydrates > 0:
                min_value = min(self.split_proportion)
                proteins_proportion = round(self.split_proteins / min_value, 2)
                fats_proportion = round(self.split_fats / min_value, 2)
                carbohydrates_proportion = round(self.split_carbohydrates / min_value, 2)
                nutrient_proportion_dict = self.__get_nutrient_proportion_dict(
                    proteins_proportion, fats_proportion, carbohydrates_proportion
                )
                return self.__get_products_group_by_proportion(nutrient_proportion_dict)

            # БЖУ выше нормы
            if self.split_proteins < 0 and self.split_fats < 0 and self.split_carbohydrates < 0:
                max_value = max(self.split_proportion)
                proteins_proportion = round(max_value / self.split_proteins, 2)
                fats_proportion = round(max_value / self.split_fats, 2)
                carbohydrates_proportion = round(max_value / self.split_carbohydrates, 2)
                nutrient_proportion_dict = self.__get_nutrient_proportion_dict(
                    proteins_proportion, fats_proportion, carbohydrates_proportion
                )
                return self.__get_products_group_by_proportion(nutrient_proportion_dict)

            # Б ниже нормы, ЖУ выше нормы
            if self.split_proteins > 0 and self.split_fats <= 0 and self.split_carbohydrates <= 0:
                proteins_proportion = abs(self.split_proteins)
                fats_proportion = 1
                carbohydrates_proportion = 1
                nutrient_proportion_dict = self.__get_nutrient_proportion_dict(
                    proteins_proportion, fats_proportion, carbohydrates_proportion
                )
                return self.__get_products_group_by_proportion(nutrient_proportion_dict)

            # Ж ниже нормы, БУ выше нормы
            if self.split_proteins <= 0 and self.split_fats > 0 and self.split_carbohydrates <= 0:
                proteins_proportion = 1
                fats_proportion = abs(self.split_fats)
                carbohydrates_proportion = 1
                nutrient_proportion_dict = self.__get_nutrient_proportion_dict(
                    proteins_proportion, fats_proportion, carbohydrates_proportion
                )
                return self.__get_products_group_by_proportion(nutrient_proportion_dict)

            # У ниже нормы, БЖ выше нормы
            if self.split_proteins <= 0 and self.split_fats <= 0 and self.split_carbohydrates > 0:
                proteins_proportion = 1
                fats_proportion = 1
                carbohydrates_proportion = abs(self.split_carbohydrates)
                nutrient_proportion_dict = self.__get_nutrient_proportion_dict(
                    proteins_proportion, fats_proportion, carbohydrates_proportion
                )
                return self.__get_products_group_by_proportion(nutrient_proportion_dict)

            # БЖ ниже нормы, У выше нормы
            if self.split_proteins > 0 and self.split_fats > 0 and self.split_carbohydrates <= 0:
                proteins_proportion = abs(self.split_proteins)
                fats_proportion = abs(self.split_fats)
                carbohydrates_proportion = 1
                nutrient_proportion_dict = self.__get_nutrient_proportion_dict(
                    proteins_proportion, fats_proportion, carbohydrates_proportion
                )
                return self.__get_products_group_by_proportion(nutrient_proportion_dict)

            # ЖУ ниже нормы, Б выше нормы
            if self.split_proteins <= 0 and self.split_fats > 0 and self.split_carbohydrates > 0:
                proteins_proportion = 1
                fats_proportion = abs(self.split_fats)
                carbohydrates_proportion = abs(self.split_carbohydrates)
                nutrient_proportion_dict = self.__get_nutrient_proportion_dict(
                    proteins_proportion, fats_proportion, carbohydrates_proportion
                )
                return self.__get_products_group_by_proportion(nutrient_proportion_dict)

            # БУ ниже нормы, Ж выше нормы
            if self.split_proteins > 0 and self.split_fats <= 0 and self.split_carbohydrates > 0:
                proteins_proportion = abs(self.split_proteins)
                fats_proportion = 1
                carbohydrates_proportion = abs(self.split_carbohydrates)
                nutrient_proportion_dict = self.__get_nutrient_proportion_dict(
                    proteins_proportion, fats_proportion, carbohydrates_proportion
                )
                return self.__get_products_group_by_proportion(nutrient_proportion_dict)
        else:
            raise ValidationError({"status": "400", "error": "There are too low eating to make recommendations"})

    def get_exclude_product(self) -> Product:
        """
        Получение рекомендованного к исключению продукта.
        """
        # Необходимо съесть минимум 3 продукта
        if len(self.eaten_products) > 2:
            return self.__find_exclude_product()
        else:
            raise ValidationError({"status": "400", "error": "There are too low eating to make recommendations"})
