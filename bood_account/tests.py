from unittest import mock

from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APITestCase, APIRequestFactory
from .models import Person
from .views import UserActivationView


class UserViewSetTest(APITestCase):
    def setUp(self) -> None:
        self.person = Person.objects.create_superuser(email="admin@admin.com", password="12345")
        self.factory = APIRequestFactory()
        self.url_jwt_create = reverse("jwt-create")
        self.url_jwt_refresh = reverse("jwt-refresh")
        self.url_user = reverse("person-list")
        self.url_user_me = reverse("person-me")

    def test_get_and_refresh_token(self) -> None:
        # Get token
        create_data = {"email": "admin@admin.com", "password": "12345"}
        response = self.client.post(self.url_jwt_create, create_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["access"])
        self.assertTrue(response.data["refresh"])

        # Refresh token
        refresh_data = {"refresh": response.data["refresh"]}
        response = self.client.post(self.url_jwt_refresh, refresh_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["access"])
        self.assertTrue(response.data["refresh"])

    def test_create_user(self) -> None:
        data = {"email": "test@mail.ru", "password": "FU7I3kf5PO34kf"}
        response = self.client.post(self.url_user, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = Person.objects.get(id=response.data["id"])
        self.assertEqual(user.email, data["email"])

    def test_create_user_manager(self) -> None:
        user = Person.objects.create_user(email="test@test.ru", password="testpassword", name="User")

        self.assertEqual(str(user), user.email)
        self.assertEqual(user.get_full_name(), user.name)
        self.assertFalse(user.has_perm(perm="IsAdmin"))
        self.assertTrue(user.has_module_perms(app_label="TestApp"))

        with self.assertRaises(ValueError):
            Person.objects.create_user(email="", password="testpassword")

    def test_create_user_with_name(self) -> None:
        data = {"email": "test2@mail.ru", "password": "FU7I3kf5PO34kf", "name": "Boris"}
        response = self.client.post(self.url_user, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = Person.objects.get(id=response.data["id"])
        self.assertEqual(user.email, data["email"])
        self.assertEqual(user.name, data["name"])

    def test_get_user(self) -> None:
        # Get token
        create_data = {"email": "admin@admin.com", "password": "12345"}
        response = self.client.post(self.url_jwt_create, create_data)
        access_token = response.data["access"]

        headers = {"Authorization": f"JWT {access_token}"}
        response = self.client.get(self.url_user_me, headers=headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, response.data["id"])
        self.assertEqual(create_data["email"], response.data["email"])

    def test_user_activation(self) -> None:
        # Create a request
        url = "/api/v1/users/activation/"
        request = self.factory.get(url)
        request.META["HTTP_HOST"] = "example.com"

        # Set protocol based on request.is_secure()
        # if request.is_secure():
        #     protocol = 'https://'
        protocol = "http://"
        web_url = protocol + request.get_host()
        post_url = web_url + url

        # Set uid and token from the URL parameters
        uid = "uid"
        token = "token"

        # Create post data
        post_data = {"uid": uid, "token": token}

        # Create a mock response
        expected_content = "Expected Response Content"
        mock_response = mock.Mock(spec=Response)
        mock_response.text = expected_content

        # Patch requests.post to return the mock response
        with mock.patch("requests.post", return_value=mock_response) as mock_post:
            # Make the GET request to UserActivationView
            response = UserActivationView.as_view()(request, uid=uid, token=token)

            # Assert requests.post is called with the expected arguments
            mock_post.assert_called_once_with(post_url, data=post_data)

            # Assert the response contains the expected content
            self.assertEqual(response.data, expected_content)
