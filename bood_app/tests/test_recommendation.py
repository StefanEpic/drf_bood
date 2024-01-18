from django.urls import reverse
from rest_framework import status

from bood_app.models import Eating
from bood_app.tests.base_classes import BaseInitTestCase


class RecommendationTestCase(BaseInitTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.token = self.get_authorization(1)
        self.url = reverse("recommendation")

    def test_get_valid_include_scenario(self) -> None:
        self.eating4 = Eating.objects.create(recipe=self.recipe, person_card=self.person_card1)
        include_product = {
            "id": 3,
            "title": "Батон",
            "proteins": 0.077,
            "fats": 0.03,
            "carbohydrates": 0.501,
            "calories": 2.59,
            "water": 0.341,
        }

        response = self.client.get(self.url, headers=self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "200")
        self.assertEqual(response.data["detail"]["products"]["include"][0]["id"], include_product["id"])
        self.assertEqual(response.data["detail"]["products"]["include"][0]["title"], include_product["title"])

    def test_get_valid_exclude_scenario(self) -> None:
        self.eating4 = Eating.objects.create(product_weight=self.productweight2, person_card=self.person_card1)
        self.eating5 = Eating.objects.create(recipe=self.recipe, person_card=self.person_card1)
        self.eating6 = Eating.objects.create(recipe=self.recipe, person_card=self.person_card1)
        self.eating7 = Eating.objects.create(recipe=self.recipe, person_card=self.person_card1)

        exclude_product = {
            "id": 2,
            "title": "Курица",
            "proteins": 0.182,
            "fats": 0.184,
            "carbohydrates": 0.0,
            "calories": 2.38,
            "water": 0.626,
        }

        response = self.client.get(self.url, headers=self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "200")
        self.assertEqual(response.data["detail"]["products"]["exclude"][0]["id"], exclude_product["id"])
        self.assertEqual(response.data["detail"]["products"]["exclude"][0]["title"], exclude_product["title"])

    def test_get_invalid_low_eating(self) -> None:
        response = self.client.get(self.url, headers=self.token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "400")
        self.assertEqual(response.data["error"], "There are too low eating to make recommendations")
