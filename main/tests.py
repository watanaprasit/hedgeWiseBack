from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
import json

class FirebaseViewsTest(TestCase):
    def setUp(self):
        self.client = Client()

    @patch('main.views.create_user')
    def test_create_firebase_user_success(self, mock_create_user):
        mock_create_user.return_value = 'User created successfully'

        response = self.client.post(
            reverse('create_firebase_user'),
            json.dumps({'email': 'test@example.com', 'password': 'testpassword'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'message': 'User created successfully'})

    def test_create_firebase_user_invalid_method(self):
        response = self.client.get(reverse('create_firebase_user'))
        self.assertEqual(response.status_code, 405)

    @patch('main.views.delete_user')
    def test_delete_firebase_user_success(self, mock_delete_user):
        mock_delete_user.return_value = 'User deleted successfully'

        response = self.client.post(
            reverse('delete_firebase_user'),
            {'uid': '12345'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'message': 'User deleted successfully'})

    def test_delete_firebase_user_missing_uid(self):
        response = self.client.post(reverse('delete_firebase_user'))
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'error': 'UID is required.'})

    @patch('main.views.get_user_by_email')
    def test_get_firebase_user_by_email_success(self, mock_get_user_by_email):
        mock_get_user_by_email.return_value = {'email': 'test@example.com'}

        response = self.client.get(reverse('get_firebase_user_by_email'), {'email': 'test@example.com'})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'user': {'email': 'test@example.com'}})

    def test_get_firebase_user_by_email_missing_email(self):
        response = self.client.get(reverse('get_firebase_user_by_email'))
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'error': 'Email is required.'})

    @patch('main.views.get_user_by_uid')
    def test_get_firebase_user_by_uid_success(self, mock_get_user_by_uid):
        mock_get_user_by_uid.return_value = {'uid': '12345'}

        response = self.client.get(reverse('get_firebase_user_by_uid'), {'uid': '12345'})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'user': {'uid': '12345'}})

    def test_get_firebase_user_by_uid_missing_uid(self):
        response = self.client.get(reverse('get_firebase_user_by_uid'))
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'error': 'UID is required.'})

    @patch('main.views.auth.get_user_by_email')
    def test_verify_firebase_token_success(self, mock_get_user_by_email):
        mock_get_user_by_email.return_value = type('User', (object,), {'uid': '12345'})()

        response = self.client.post(
            reverse('verify_firebase_token'),
            json.dumps({'email': 'test@example.com', 'password': 'testpassword'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'status': 'success', 'user_id': '12345'})

    def test_verify_firebase_token_invalid_method(self):
        response = self.client.get(reverse('verify_firebase_token'))
        self.assertEqual(response.status_code, 405)

