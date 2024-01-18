from django.urls import reverse
from rest_framework import status

from bood_app.models import Eating
from bood_app.tests.base_classes import BaseInitTestCase


class EatingTestCase(BaseInitTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.token = self.get_authorization(1)
        self.url = reverse("eating-list")
        self.url_detail = reverse("eating-detail", args=(self.eating1.id,))

    def test_model(self) -> None:
        self.assertEqual(str(self.eating1), self.eating1.person_card.person.email)
        self.assertEqual(str(self.productweight1), self.productweight1.product.title)
        self.assertEqual(str(self.water1), str(self.water1.weight))

    def test_get_valid(self) -> None:
        response = self.client.get(self.url, headers=self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["results"][0]["product_weight"])

    def test_get_detail_valid(self) -> None:
        response = self.client.get(self.url_detail, headers=self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["product_weight"])

    def test_post_valid_product(self) -> None:
        data = {"product_weight": {"product": 1, "weight": 120}}
        response = self.client.post(self.url, data, headers=self.token, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "200")
        self.assertEqual(response.data["detail"]["product_weight"]["product"], 1)
        self.assertEqual(response.data["detail"]["product_weight"]["weight"], 120)
        self.assertFalse(response.data["detail"]["recipe"])
        self.assertFalse(response.data["detail"]["water"])

    def test_post_valid_recipe(self) -> None:
        data = {"recipe": 1}
        response = self.client.post(self.url, data, headers=self.token, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "200")
        self.assertFalse(response.data["detail"]["product_weight"], None)
        self.assertEqual(response.data["detail"]["recipe"], 1)
        self.assertFalse(response.data["detail"]["water"], None)

    def test_post_valid_water(self) -> None:
        data = {"water": {"weight": 200}}
        response = self.client.post(self.url, data, headers=self.token, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "200")
        self.assertFalse(response.data["detail"]["product_weight"], None)
        self.assertFalse(response.data["detail"]["recipe"], None)
        self.assertEqual(response.data["detail"]["water"]["weight"], 200)

    def test_post_invalid_two_elements(self) -> None:
        data = {"product_weight": {"product": 1, "weight": 120}, "water": {"weight": 200}}
        response = self.client.post(self.url, data, headers=self.token, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "400")
        self.assertEqual(response.data["error"], "only one value can be passed (product_weight, recipe or water)")

    def test_post_invalid_zero_elements(self) -> None:
        data = {}
        response = self.client.post(self.url, data, headers=self.token, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "400")
        self.assertEqual(response.data["error"], "product_weight, recipe and water cannot be NULL at the same time")

    def test_patch_valid(self) -> None:
        data = {"water": {"weight": 200}}
        response = self.client.patch(self.url_detail, data, headers=self.token, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "200")
        self.assertEqual(response.data["detail"]["water"]["weight"], 200)
        self.assertFalse(response.data["detail"]["product_weight"])
        self.assertFalse(response.data["detail"]["recipe"])

    def test_patch_invalid_two_elements(self) -> None:
        data = {"product_weight": {"product": 1, "weight": 120}, "water": {"weight": 200}}
        response = self.client.patch(self.url_detail, data, headers=self.token, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "400")
        self.assertEqual(response.data["error"], "only one value can be passed (product_weight, recipe or water)")

    def test_patch_invalid_zero_elements(self) -> None:
        data = {}
        response = self.client.patch(self.url_detail, data, headers=self.token, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "400")
        self.assertEqual(response.data["error"], "product_weight, recipe and water cannot be NULL at the same time")

    def test_patch_valid_switch_water_to_product(self) -> None:
        url_patch = reverse("eating-detail", args=(self.eating3.id,))
        data = {"product_weight": {"product": 1, "weight": 120}}
        response = self.client.patch(url_patch, data, headers=self.token, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "200")
        self.assertEqual(response.data["detail"]["id"], self.eating3.id)
        self.assertEqual(response.data["detail"]["product_weight"], data["product_weight"])
        self.assertFalse(response.data["detail"]["recipe"])
        self.assertFalse(response.data["detail"]["water"])

    def test_patch_valid_switch_product_to_recipe(self) -> None:
        data = {"recipe": 1}
        response = self.client.patch(self.url_detail, data, headers=self.token, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "200")
        self.assertEqual(response.data["detail"]["id"], self.eating1.id)
        self.assertEqual(response.data["detail"]["recipe"], data["recipe"])
        self.assertFalse(response.data["detail"]["product_weight"])
        self.assertFalse(response.data["detail"]["water"])

    def test_delete_valid(self) -> None:
        response = self.client.delete(self.url_detail, headers=self.token)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_signal(self) -> None:
        self.eating1.delete()
        self.assertEqual(len(Eating.objects.all()), 2)
