from django.urls import reverse
from rest_framework import status
from bood_app.tests.base_classes import BaseInitTestCase


class FemaleTypeTestCase(BaseInitTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.token = self.get_authorization(1)
        self.url = reverse("femaletypes-list")

    def test_model(self) -> None:
        self.assertEqual(str(self.femaletype), self.femaletype.title)

    def test_get_valid(self) -> None:
        response = self.client.get(self.url, headers=self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["results"][0]["title"])
