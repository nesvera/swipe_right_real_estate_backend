"""
Tests for user API.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

REFRESH_URL = reverse("user:refresh")


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


class PublicApiTests(TestCase):
    """Test public features of user API."""

    def test_create_user_success(self):
        """Test creating a user is successful."""
        payload = {
            "email": "test@example.com",
            "password": "Mysecure123$",
            "name": "my user",
        }
        client = APIClient()
        url = reverse("user:create")
        res = client.post(url, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertNotIn("password", res.data)

        user = get_user_model().objects.get(email=payload.get("email"))
        self.assertTrue(user.check_password(payload.get("password")))

    def test_user_with_email_exists_error(self):
        """Test error returned if user with email already exists."""
        payload = {
            "email": "test@example.com",
            "password": "mysecure123",
            "name": "my user",
        }
        create_user(**payload)

        client = APIClient()
        url = reverse("user:create")
        res = client.post(url, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test an error is returned if password is too short."""
        payload = {"email": "test@example.com", "password": "pw", "name": "my name"}

        client = APIClient()
        url = reverse("user:create")
        res = client.post(url, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = (
            get_user_model().objects.filter(email=payload.get("email")).exists()
        )
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test generates token for valid credentials."""
        user_details = {
            "name": "my user",
            "email": "myuser@myemail.com",
            "password": "test123456",
        }
        create_user(**user_details)

        payload = {
            "email": user_details.get("email"),
            "password": user_details.get("password"),
        }

        client = APIClient()
        url = reverse("user:auth")
        res = client.post(url, payload)

        self.assertIn("refresh", res.data)
        self.assertIn("access", res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        """Test returns error if credentials are invalid."""
        create_user(email="myuser@myemail.com", password="securepassword")

        payload = {"email": "myuser@myemail.com", "password": "notsecure"}

        client = APIClient()
        url = reverse("user:auth")
        res = client.post(url, payload)

        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_token_blank_password(self):
        """Test authentication without password raises error."""
        payload = {"email": "myuser@myemail.com", "password": ""}

        client = APIClient()
        url = reverse("user:auth")
        res = client.post(url, payload)

        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test authentication is required for users."""
        user = create_user(
            email="myuser@myemail.com", password="Securepassword123$", name="My user"
        )

        client = APIClient()
        url = reverse("user:user_info")
        res = client.get(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateApiTests(TestCase):
    """Test API requests that require authentication."""

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = create_user(
            email="myuser@myemail.com", password="Securepassword123$", name="My user"
        )

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user."""
        client = APIClient()
        client.force_authenticate(user=self.user)

        url = reverse("user:user_info")
        res = client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        user_id = res.data.get("id")
        user_name = res.data.get("name")
        user_email = res.data.get("email")

        self.assertEqual(user_id, str(self.user.id))
        self.assertEqual(user_name, self.user.name)
        self.assertEqual(user_email, self.user.email)

    def test_post_me_not_allowed(self):
        """Test POST is not allowed for the me endpoint."""
        client = APIClient()
        client.force_authenticate(user=self.user)

        url = reverse("user:user_info")
        res = client.post(url, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_partial_update_only_user_name(self):
        """Test updating user profile."""
        payload = {
            "name": "new name",
        }

        client = APIClient()
        client.force_authenticate(user=self.user)

        url = reverse("user:user_info")
        res = client.patch(url, payload)

        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.name, payload.get("name"))

    def test_partial_update_only_user_password(self):
        """Test updating user profile."""
        payload = {"password": "Newpassword123$"}

        client = APIClient()
        client.force_authenticate(user=self.user)

        url = reverse("user:user_info")
        res = client.patch(url, payload)

        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.check_password(payload.get("password")))

    def test_partial_update_user_profile(self):
        """Test updating user profile."""
        payload = {"name": "new name", "password": "Newpassword123$"}

        client = APIClient()
        client.force_authenticate(user=self.user)

        url = reverse("user:user_info")
        res = client.patch(url, payload)

        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.name, payload.get("name"))
        self.assertTrue(self.user.check_password(payload.get("password")))

    def test_partial_update_user_fail_bad_password(self):
        """Test updating user profile with password not matching security policy"""
        payload = {"name": "new name", "password": "Newpassw"}

        client = APIClient()
        client.force_authenticate(user=self.user)

        url = reverse("user:user_info")
        res = client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
