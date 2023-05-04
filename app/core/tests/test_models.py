"""
    Test cases for models
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from core.models import Recepie, Tag


def create_user(**params):
    """Helper function to create user"""
    return get_user_model().objects.create_user(**params)


class ModelTests(TestCase):
    """Test cases for models"""

    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful"""
        email = 'test@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password)
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized"""
        sample_emails = [
            ["test1@ExamplE.com", "test1@example.com"],
            ["TEST2@EXAMPLE.COM", "TEST2@example.com"]
        ]
        for sample_email, expected_email in sample_emails:
            user = get_user_model().objects.create_user(
                email=sample_email,
                password='testpass123')
            print(user.email, expected_email)
            self.assertEqual(user.email, expected_email)

    def test_new_user_without_email(self):
        """Test creating user without email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email=None,
                password='testpass123')

    def test_create_new_superuser(self):
        """Test creating a new superuser"""
        user = get_user_model().objects.create_superuser(
            email='super@example.com',
            password='testpass123'
        )
        self.assertTrue(user.is_superuser)

    def test_create_recepie(self):
        """Test creating a new recepie"""
        email = 'test@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password)
        recepie = Recepie.objects.create(
            title="Test recepie",
            price=Decimal(10.00),
            description="Test description",
            time_minutes=5,
            user=user
        )
        self.assertEqual(recepie.title, "Test recepie")
        self.assertEqual(recepie.price, Decimal(10.00))
        self.assertEqual(recepie.description, "Test description")

    def test_create_tags(self):
        """Test creating a new tag"""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test name'
        }
        user = create_user(**payload)
        tag = Tag.objects.create(user=user, name="Test tag")
        self.assertEqual(tag.name, "Test tag")