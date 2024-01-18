from django.urls import reverse
from rest_framework import status

from bood_app.models import PersonCard, Measurement
from bood_app.tests.base_classes import BaseInitTestCase


class CalculateTestCase(BaseInitTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.token = self.get_authorization(1)
        self.url_standard = reverse("standard")
        self.url_current = reverse("current")

    def test_get_valid_standard_male(self) -> None:
        standard_data = {
            "imt_type": "Эктоморф",
            "imt_value": 26.1,
            "calories": 2173,
            "proteins": 61,
            "fats": 53,
            "carbohydrates": 225,
            "water": 2400,
        }
        response = self.client.get(self.url_standard, headers=self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "200")
        self.assertEqual(response.data["detail"], standard_data)

    def test_get_valid_standard_female(self) -> None:
        person_card2 = PersonCard.objects.create(
            height=165,
            age=25,
            gender="female",
            activity=1.2,
            person=self.person2,
        )
        Measurement.objects.create(
            weight=80,
            chest=100,
            waist=70,
            hips=90,
            hand=16,
            person_card=person_card2,
        )
        token = self.get_authorization(2)
        standard_data = {
            "imt_type": "Мезоморф",
            "imt_value": 29.4,
            "calories": 1843,
            "proteins": 51,
            "fats": 45,
            "carbohydrates": 191,
            "water": 2400,
        }
        response = self.client.get(self.url_standard, headers=token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "200")
        self.assertEqual(response.data["detail"], standard_data)

    def test_get_valid_current(self) -> None:
        current_data = {
            "imt_type": "Эктоморф",
            "imt_value": 26.1,
            "calories": 497,
            "proteins": 26,
            "fats": 21,
            "carbohydrates": 50,
            "water": 197,
        }
        response = self.client.get(self.url_current, headers=self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "200")
        self.assertEqual(response.data["detail"], current_data)

    def test_get_invalid_date(self) -> None:
        url = self.url_current + "?date=1234"
        response = self.client.get(url, headers=self.token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "400")
        self.assertEqual(response.data["error"], "Invalid date format")

    def test_get_invalid_no_measurements(self) -> None:
        PersonCard.objects.create(
            height=165,
            age=25,
            gender="female",
            activity=1.2,
            person=self.person2,
        )
        token = self.get_authorization(2)
        response = self.client.get(self.url_standard, headers=token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "400")
        self.assertEqual(response.data["error"], "Measurements not found")
