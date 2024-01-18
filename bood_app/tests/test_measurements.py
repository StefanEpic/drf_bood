from django.urls import reverse
from rest_framework import status
from bood_app.tests.base_classes import BaseInitTestCase


class MeasurementTestCase(BaseInitTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.token = self.get_authorization(1)
        self.url = reverse("measurements-list")
        self.url_detail = reverse("measurements-detail", args=(self.measurement.id,))

    def test_model(self) -> None:
        self.assertEqual(str(self.measurement), self.person_card1.person.email)

    def test_get_valid(self) -> None:
        response = self.client.get(self.url, headers=self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["results"][0]["weight"])

    def test_get_detail_valid(self) -> None:
        response = self.client.get(self.url_detail, headers=self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["weight"])

    def test_post_valid(self) -> None:
        data = {"weight": 80, "chest": 100, "waist": 70, "hips": 90, "hand": 16}
        response = self.client.post(self.url, data, headers=self.token, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "200")
        self.assertEqual(response.data["detail"]["weight"], data["weight"])
        self.assertEqual(response.data["detail"]["chest"], data["chest"])
        self.assertEqual(response.data["detail"]["waist"], data["waist"])
        self.assertEqual(response.data["detail"]["hips"], data["hips"])
        self.assertEqual(response.data["detail"]["hand"], data["hand"])

    def test_post_invalid_weight(self) -> None:
        data = {"weight": 600, "chest": 100, "waist": 70, "hips": 90, "hand": 16}
        response = self.client.post(self.url, data, headers=self.token, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "400")
        self.assertTrue(response.data["error"]["weight"])

    def test_post_invalid_chest(self) -> None:
        data = {"weight": 80, "chest": 600, "waist": 70, "hips": 90, "hand": 16}
        response = self.client.post(self.url, data, headers=self.token, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "400")
        self.assertTrue(response.data["error"]["chest"])

    def test_post_invalid_waist(self) -> None:
        data = {"weight": 80, "chest": 100, "waist": 600, "hips": 90, "hand": 16}
        response = self.client.post(self.url, data, headers=self.token, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "400")
        self.assertTrue(response.data["error"]["waist"])

    def test_post_invalid_hips(self) -> None:
        data = {"weight": 80, "chest": 100, "waist": 70, "hips": 600, "hand": 16}
        response = self.client.post(self.url, data, headers=self.token, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "400")
        self.assertTrue(response.data["error"]["hips"])

    def test_post_invalid_hand(self) -> None:
        data = {"weight": 80, "chest": 100, "waist": 70, "hips": 90, "hand": 600}
        response = self.client.post(self.url, data, headers=self.token, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "400")
        self.assertTrue(response.data["error"]["hand"])

    def test_post_invalid_not_person_card(self) -> None:
        data = {"weight": 80, "chest": 100, "waist": 70, "hips": 90, "hand": 16}
        token = self.get_authorization(2)
        response = self.client.post(self.url, data, headers=token, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "400")
        self.assertEqual(response.data["error"], "Person card not found")

    def test_patch_valid(self) -> None:
        data = {"weight": 90, "chest": 90}
        response = self.client.patch(self.url_detail, data, headers=self.token, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "200")
        self.assertEqual(response.data["detail"]["weight"], data["weight"])
        self.assertEqual(response.data["detail"]["chest"], data["chest"])

    def test_delete_valid(self) -> None:
        response = self.client.delete(self.url_detail, headers=self.token)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
