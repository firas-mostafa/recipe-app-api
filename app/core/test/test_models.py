# Test Models
from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    # Test models.
    def test_create_user_with_email_successful(self):
        email = 'test@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(email, password)
        self.assertEqual(user.email, email)
        self.assertTrue(
            user.check_password(password)
        )

    def test_new_user_email_normalized(self):
        # Test email is normalized for new user
        sample_email = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@EXAMPLE.COM', 'test4@example.com'],
            ['test5@EXAMPLE.Com', 'test5@example.com'],
        ]
        for email, expected in sample_email:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        # Test new user without email raises a ValueError
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', "test123")

    def test_create_superuser(self):
        # Test creating a superuser/admin
        user = get_user_model().objects.create_superuser(
            'admin@admin.com',
            'admin123'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
