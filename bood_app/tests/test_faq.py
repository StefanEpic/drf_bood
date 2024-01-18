from django.urls import reverse
from rest_framework import status
from bood_app.tests.base_classes import BaseInitTestCase


class FAQTestCase(BaseInitTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.token = self.get_authorization(1)
        self.url = reverse("faq-list")

    def test_model(self) -> None:
        self.assertEqual(str(self.faq), self.faq.question)

    def test_get_valid(self) -> None:
        response = self.client.get(self.url, headers=self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["results"][0]["question"])
