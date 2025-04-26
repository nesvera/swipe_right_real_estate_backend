""""
Tets for models.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful."""
        email = "test@myemail.com"
        password = "mysecurepassword"
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            ["test1@MYEMAIL.com", "test1@myemail.com"],
            ["Test2@myemail.com", "Test2@myemail.com"],
            ["TEST3@myemail.COM", "TEST3@myemail.com"],
        ]

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(
                email=email, password="mysecurepassword"
            )
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without email raises a ValuError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user("", "mypassword")

    def test_create_super_user(self):
        """Test creating a superuser."""
        user = get_user_model().objects.create_superuser(
            email="my@email.com", password="mypassword"
        )
        self.assertTrue(user.is_superuser)
