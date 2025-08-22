# Test for user api
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from PIL import Image
from rest_framework.test import APIClient
from rest_framework import status
import tempfile
import os

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')
IMAGE_UPLOAD_URL = reverse('user:user-upload-image')


def create_user(**params):
    # Create and return a now user
    return get_user_model().objects.create_user(**params)


class PublicUserAPITests(TestCase):
    # Test the public features of the user API

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        # Test creating user is  successfull
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test User',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_with_email_exists_error(self):
        # Test return error if user with email exists
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test User',
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_is_too_short_error(self):
        # Test return error if password is less than 5 char
        payload = {
            'email': 'testforpassword@example.com',
            'password': 'ts',
            'name': 'Test User',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
            ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        # Test create token for user
        user_details = {
            'name': 'Test Name',
            'email': 'testemail@example.com',
            'password': 'passtest123',
        }
        create_user(**user_details)
        payload = {
            'email': user_details['email'],
            'password': user_details['password']
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        # Test Create Token Bad Credentials
        create_user(email='test@example.com', password='testpass123')
        payload = {
            'email': 'test@example.com',
            'password': 'wrongpass',
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_blank_password_return_error(self):
        # Test posting a blank password returns an error
        payload = {
            'email': 'test@example.com',
            'password': '',
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        # Test authentication is required for users
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    # Test the private features of the user API

    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password='test123pass',
            name='Test Name'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_sccess(self):
        # Test retrieving profile for logged in user
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email,
            'image': self.user.image,
        })

    def test_post_me_not_allowed(self):
        # Test POST is not allowed for the me endpoint
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        # Test updating the user profile for the authenticated user
        payload = {'name': 'Updated name', 'password': 'newpass123'}
        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)


class ImageUploadTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@example.com'
            'password123'
        )
        self.client.force_authenticate(self.user)

    def tearDown(self):
        self.user.image.delete()

    def test_upload_image(self):
        url = IMAGE_UPLOAD_URL
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new('RGB', (10, 10))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            payload = {'image': image_file}
            res = self.client.post(url, payload, format='multipart')
            self.user.refresh_from_db()

            self.assertEqual(res.status_code, status.HTTP_200_OK)
            self.assertIn('image', res.data)
            self.assertTrue(os.path.exists(self.user.image.path))

    def test_upload_image_bad_request(self):
        url = IMAGE_UPLOAD_URL
        payload = {'image': 'notanImage'}
        res = self.client.post(url, payload, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
