from django.urls import reverse
from rest_framework import status
from bood_app.tests.base_classes import BaseInitTestCase


class RecipeTestCase(BaseInitTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.token = self.get_authorization(1)
        self.url = reverse("recipes-list")
        self.url_detail = reverse("recipes-detail", args=(self.recipe.id,))

    def test_model(self) -> None:
        self.assertEqual(str(self.recipe), self.recipe.title)

    def test_get_valid(self) -> None:
        response = self.client.get(self.url, headers=self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["results"][0]["title"])

    def test_get_detail_valid(self) -> None:
        response = self.client.get(self.url_detail, headers=self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["title"])

    def test_post_invalid_product(self) -> None:
        data = {"title": "Test", "description": "", "image": "", "product_weight": [{"product": 999, "weight": 40}]}
        response = self.client.post(self.url, data, headers=self.token, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "400")
        self.assertTrue(response.data["error"]["product_weight"][0]["product"])

    def test_post_valid_product(self) -> None:
        data = {
            "title": "Test",
            "description": "",
            "image": "",
            "product_weight": [
                {"product": 1, "weight": 40},
                {"product": 2, "weight": 80},
            ],
        }
        response = self.client.post(self.url, data, headers=self.token, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "200")
        self.assertEqual(response.data["detail"]["title"], data["title"])
        self.assertEqual(response.data["detail"]["description"], data["description"])
        self.assertEqual(response.data["detail"]["image"], data["image"])
        self.assertEqual(response.data["detail"]["product_weight"], data["product_weight"])

    def test_post_valid_identical_product(self) -> None:
        data = {
            "title": "Test",
            "description": "",
            "image": "",
            "product_weight": [
                {"product": 1, "weight": 40},
                {"product": 1, "weight": 80},
            ],
        }
        response = self.client.post(self.url, data, headers=self.token, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "200")
        self.assertEqual(response.data["detail"]["title"], data["title"])
        self.assertEqual(response.data["detail"]["description"], data["description"])
        self.assertEqual(response.data["detail"]["image"], data["image"])
        self.assertEqual(response.data["detail"]["product_weight"][0]["weight"], 40)
        self.assertEqual(response.data["detail"]["product_weight"][1]["weight"], 80)

    def test_post_invalid_zero_product(self) -> None:
        data = {"title": "Test", "description": "", "image": "", "product_weight": []}
        response = self.client.post(self.url, data, headers=self.token, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "400")
        self.assertEqual(response.data["error"], "Product not found")

    def test_patch_valid(self) -> None:
        data = {"title": "TestPatch", "product_weight": [{"product": 1, "weight": 20}]}
        response = self.client.patch(self.url_detail, data, headers=self.token, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "200")
        self.assertEqual(response.data["detail"]["title"], data["title"])
        self.assertEqual(response.data["detail"]["product_weight"], data["product_weight"])

    def test_patch_valid_identical_product(self) -> None:
        data = {
            "title": "TestPatch",
            "product_weight": [
                {"product": 1, "weight": 40},
                {"product": 1, "weight": 80},
            ],
        }
        response = self.client.patch(self.url_detail, data, headers=self.token, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "200")
        self.assertEqual(response.data["detail"]["title"], data["title"])
        self.assertEqual(response.data["detail"]["product_weight"][0]["weight"], 40)
        self.assertEqual(response.data["detail"]["product_weight"][1]["weight"], 80)

    def test_delete_valid(self) -> None:
        response = self.client.delete(self.url_detail, headers=self.token)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
