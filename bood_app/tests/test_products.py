from django.urls import reverse
from rest_framework import status

from bood_app.models import Vitamin, MicroElement
from bood_app.tests.base_classes import BaseInitTestCase


class ProductTestCase(BaseInitTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.token = self.get_authorization(1)
        self.url = reverse("products-list")
        self.url_category = reverse("products_category-list")

    def test_model(self) -> None:
        self.assertEqual(str(self.product1), self.product1.title)
        self.assertEqual(str(self.vitamin1), f"Витамины для: {self.vitamin1.product.title}")
        self.assertEqual(str(self.microelement1), f"Микроэлементы для: {self.microelement1.product.title}")
        self.assertEqual(str(self.category1), self.category1.title)

    def test_get_valid_products(self) -> None:
        response = self.client.get(self.url, headers=self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["results"][0]["title"])

    def test_get_valid_category(self) -> None:
        response = self.client.get(self.url_category, headers=self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["results"][0]["title"])

    def test_signal(self) -> None:
        self.product1.delete()
        self.assertFalse(Vitamin.objects.filter(id=1))
        self.assertFalse(MicroElement.objects.filter(id=1))
