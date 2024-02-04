from django.urls import reverse
from rest_framework import status

from bood_app.models import Eating, ProductWeight
from bood_app.tests.base_classes import BaseInitTestCase


class RecommendationTestCase(BaseInitTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.token = self.get_authorization(1)
        self.url_include = reverse("recommendation_include")
        self.url_exclude = reverse("recommendation_exclude")

    def test_get_valid_include_first_scenario(self) -> None:
        # БЖУ ниже нормы
        self.eating4 = Eating.objects.create(recipe=self.recipe, person_card=self.person_card1)
        product = {
            "id": 3,
            "title": "Батон",
            "proteins": 0.077,
            "fats": 0.03,
            "carbohydrates": 0.501,
            "calories": 2.59,
            "water": 0.341,
        }

        response = self.client.get(self.url_include, headers=self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "200")
        self.assertEqual(response.data["detail"]["products"][0]["id"], product["id"])
        self.assertEqual(response.data["detail"]["products"][0]["title"], product["title"])

    def test_get_valid_include_second_scenario(self) -> None:
        # БЖУ выше нормы
        self.productweight3 = ProductWeight.objects.create(weight=300, product=self.product1, recipe=self.recipe)
        self.productweight4 = ProductWeight.objects.create(weight=300, product=self.product2, recipe=self.recipe)
        self.productweight5 = ProductWeight.objects.create(weight=300, product=self.product3, recipe=self.recipe)
        self.eating4 = Eating.objects.create(recipe=self.recipe, person_card=self.person_card1)
        self.eating5 = Eating.objects.create(product_weight=self.productweight3, person_card=self.person_card1)
        self.eating6 = Eating.objects.create(product_weight=self.productweight4, person_card=self.person_card1)
        self.eating7 = Eating.objects.create(product_weight=self.productweight5, person_card=self.person_card1)
        product = {
            "id": 3,
            "title": "Батон",
            "proteins": 0.077,
            "fats": 0.03,
            "carbohydrates": 0.501,
            "calories": 2.59,
            "water": 0.341,
        }

        response = self.client.get(self.url_include, headers=self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "200")
        self.assertEqual(response.data["detail"]["products"][0]["id"], product["id"])
        self.assertEqual(response.data["detail"]["products"][0]["title"], product["title"])

    def test_get_valid_include_thed_scenario(self) -> None:
        # У ниже нормы, БЖ выше нормы
        self.eating4 = Eating.objects.create(recipe=self.recipe, person_card=self.person_card1)
        self.eating5 = Eating.objects.create(recipe=self.recipe, person_card=self.person_card1)
        self.eating6 = Eating.objects.create(recipe=self.recipe, person_card=self.person_card1)
        product = {
            "id": 3,
            "title": "Батон",
            "proteins": 0.077,
            "fats": 0.03,
            "carbohydrates": 0.501,
            "calories": 2.59,
            "water": 0.341,
        }

        response = self.client.get(self.url_include, headers=self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "200")
        self.assertEqual(response.data["detail"]["products"][0]["id"], product["id"])
        self.assertEqual(response.data["detail"]["products"][0]["title"], product["title"])

    def test_get_valid_include_four_scenario(self) -> None:
        # БУ ниже нормы, Ж выше нормы
        self.productweight3 = ProductWeight.objects.create(weight=170, product=self.product2)
        self.eating4 = Eating.objects.create(product_weight=self.productweight3, person_card=self.person_card1)
        product = {
            "id": 1,
            "title": "Лук",
            "proteins": 0.014,
            "fats": 0.002,
            "carbohydrates": 0.082,
            "calories": 0.41,
            "water": 0.86,
        }

        response = self.client.get(self.url_include, headers=self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "200")
        self.assertEqual(response.data["detail"]["products"][0]["id"], product["id"])
        self.assertEqual(response.data["detail"]["products"][0]["title"], product["title"])

    def test_get_valid_exclude_scenario(self) -> None:
        self.eating4 = Eating.objects.create(recipe=self.recipe, person_card=self.person_card1)
        product = {
            "id": 2,
            "title": "Курица",
            "proteins": 0.182,
            "fats": 0.184,
            "carbohydrates": 0.0,
            "calories": 2.38,
            "water": 0.626,
        }

        response = self.client.get(self.url_exclude, headers=self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "200")
        self.assertEqual(response.data["detail"]["product"]["id"], product["id"])
        self.assertEqual(response.data["detail"]["product"]["title"], product["title"])

    def test_get_invalid_low_eating_include(self) -> None:
        response = self.client.get(self.url_include, headers=self.token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "400")
        self.assertEqual(response.data["error"], "There are too low eating to make recommendations")

    def test_get_invalid_low_eating_exclude(self) -> None:
        response = self.client.get(self.url_exclude, headers=self.token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "400")
        self.assertEqual(response.data["error"], "There are too low eating to make recommendations")
