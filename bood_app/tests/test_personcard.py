from django.urls import reverse
from rest_framework import status
from bood_app.tests.base_classes import BaseInitTestCase


class PersonCardTestCase(BaseInitTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.token = self.get_authorization(1)
        self.url = reverse("person_card-list")
        self.url_detail = reverse("person_card-detail", args=(self.person_card1.id,))

    def test_model(self) -> None:
        self.assertEqual(str(self.person_card1), self.person_card1.person.email)

    def test_get_valid(self) -> None:
        response = self.client.get(self.url, headers=self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["results"][0]["height"])

    def test_post_valid(self) -> None:
        data = {
            "height": 175,
            "age": 30,
            "gender": "male",
            "activity": "1.2",
            "femaletype": [],
            "exclude_products": [1],
            "exclude_category": [2],
        }
        token = self.get_authorization(2)
        response = self.client.post(self.url, data, headers=token, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "200")
        self.assertEqual(response.data["detail"]["height"], data["height"])
        self.assertEqual(response.data["detail"]["age"], data["age"])
        self.assertEqual(response.data["detail"]["gender"], data["gender"])
        self.assertEqual(response.data["detail"]["activity"], data["activity"])
        self.assertEqual(response.data["detail"]["femaletype"], data["femaletype"])
        self.assertEqual(response.data["detail"]["exclude_products"], data["exclude_products"])
        self.assertEqual(response.data["detail"]["exclude_category"], data["exclude_category"])

    def test_post_invalid_already_have(self) -> None:
        data = {
            "height": 175,
            "age": 30,
            "gender": "male",
            "activity": "1.2",
            "femaletype": [],
            "exclude_products": [1],
            "exclude_category": [2],
        }
        response = self.client.post(self.url, data, headers=self.token, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "400")
        self.assertEqual(response.data["error"], "You already have person card")

    def test_post_invalid_height(self) -> None:
        data = {
            "height": 600,
            "age": 30,
            "gender": "male",
            "activity": "1.2",
            "femaletype": [],
            "exclude_products": [1],
            "exclude_category": [2],
        }
        token = self.get_authorization(2)
        response = self.client.post(self.url, data, headers=token, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "400")
        self.assertTrue(response.data["error"]["height"])

    def test_post_invalid_age(self) -> None:
        data = {
            "height": 175,
            "age": 200,
            "gender": "male",
            "activity": "1.2",
            "femaletype": [],
            "exclude_products": [1],
            "exclude_category": [2],
        }
        token = self.get_authorization(2)
        response = self.client.post(self.url, data, headers=token, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "400")
        self.assertTrue(response.data["error"]["age"])

    def test_post_invalid_gender(self) -> None:
        data = {
            "height": 175,
            "age": 30,
            "gender": "dog",
            "activity": "1.2",
            "femaletype": [],
            "exclude_products": [1],
            "exclude_category": [2],
        }
        token = self.get_authorization(2)
        response = self.client.post(self.url, data, headers=token, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "400")
        self.assertTrue(response.data["error"]["gender"])

    def test_post_invalid_femaletype_for_male(self) -> None:
        data = {
            "height": 175,
            "age": 30,
            "gender": "male",
            "activity": "1.2",
            "femaletype": [1],
            "exclude_products": [1],
            "exclude_category": [2],
        }
        token = self.get_authorization(2)
        response = self.client.post(self.url, data, headers=token, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "400")
        self.assertEqual(response.data["error"], "Male gender can't have female type")

    def test_post_invalid_activity(self) -> None:
        data = {
            "height": 175,
            "age": 30,
            "gender": "male",
            "activity": "5",
            "femaletype": [],
            "exclude_products": [1],
            "exclude_category": [2],
        }
        token = self.get_authorization(2)
        response = self.client.post(self.url, data, headers=token, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "400")
        self.assertTrue(response.data["error"]["activity"])

    def test_post_invalid_fameletype(self) -> None:
        data = {
            "height": 175,
            "age": 30,
            "gender": "male",
            "activity": "1.2",
            "femaletype": [3],
            "exclude_products": [1],
            "exclude_category": [2],
        }
        token = self.get_authorization(2)
        response = self.client.post(self.url, data, headers=token, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "400")
        self.assertTrue(response.data["error"]["femaletype"])

    def test_post_invalid_exclude_products(self) -> None:
        data = {
            "height": 175,
            "age": 30,
            "gender": "male",
            "activity": "1.2",
            "femaletype": [],
            "exclude_products": [8],
            "exclude_category": [2],
        }
        token = self.get_authorization(2)
        response = self.client.post(self.url, data, headers=token, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "400")
        self.assertTrue(response.data["error"]["exclude_products"])

    def test_post_invalid_exclude_category(self) -> None:
        data = {
            "height": 175,
            "age": 30,
            "gender": "male",
            "activity": "1.2",
            "femaletype": [],
            "exclude_products": [1],
            "exclude_category": [8],
        }
        token = self.get_authorization(2)
        response = self.client.post(self.url, data, headers=token, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "400")
        self.assertTrue(response.data["error"]["exclude_category"])

    def test_patch_valid(self) -> None:
        data = {"height": 185, "age": 25}
        response = self.client.patch(self.url_detail, data, headers=self.token, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "200")
        self.assertEqual(response.data["detail"]["height"], data["height"])
        self.assertEqual(response.data["detail"]["age"], data["age"])

    def test_delete_valid(self) -> None:
        response = self.client.delete(self.url_detail, headers=self.token)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
