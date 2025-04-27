from django.test import SimpleTestCase
from parameterized import parameterized

from user.utils import validate_password


class PasswordValidation(SimpleTestCase):
    """
        Tests for password validation
        Test methodologies:
            - Equivalence partitioning
            - Boundary value analysis

        Equivalence partitioning
            - Valid group:
                - Passwords that meet all criteria
            - Invalid groups:
                - Too short (less than 8 characters)
                - Missing uppercase
                - Missing lowercase
                - Missing number
                - Missing special character

        Boundary value analysis
            - Password with 7 characters must fail
            - Password with 8 characters must pass
    """

    @parameterized.expand(
        [
            ("Good$123", True),
            ("Go#1", False),
            ("good$123", False),
            ("GOOD$123", False),
            ("GOOD$goo", False),
            ("Good1234", False),
            ("Good$12", False),
            ("Good$12345", True),
        ]
    )
    def test_password_validation(self, password, expected_validation_result):
        is_valid = validate_password(password=password)
        self.assertEqual(is_valid, expected_validation_result)
