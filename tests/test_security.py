from django.test import TestCase, Client
from django.urls import reverse

from users.models import User


class CsrfTest(TestCase):
    def test_login_without_csrf_fails(self):
        client = Client(enforce_csrf_checks=True)
        response = client.post(reverse('login'), {
            'username': 'test',
            'password': 'test',
        })
        self.assertEqual(response.status_code, 403)

    def test_login_with_csrf_works(self):
        User.objects.create_user(username='testuser', password='TestPass123!')
        client = Client(enforce_csrf_checks=True)
        response = client.get(reverse('login'))
        csrf_token = response.cookies.get('csrftoken')
        if csrf_token:
            token = csrf_token.value
        else:
            # Извлечь из формы
            import re
            match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', response.content.decode())
            token = match.group(1) if match else ''
        response = client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'TestPass123!',
            'csrfmiddlewaretoken': token,
        })
        self.assertIn(response.status_code, [200, 302])


class SecurityHeadersTest(TestCase):
    """Проверка что Django отдаёт security-related заголовки."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='TestPass123!'
        )
        self.client = Client()
        self.client.login(username='testuser', password='TestPass123!')

    def test_x_content_type_options(self):
        response = self.client.get(reverse('objects:map'))
        self.assertEqual(
            response.get('X-Content-Type-Options', ''), 'nosniff',
        )

    def test_x_frame_options(self):
        response = self.client.get(reverse('objects:map'))
        self.assertIn(
            response.get('X-Frame-Options', '').upper(),
            ['DENY', 'SAMEORIGIN'],
        )


class InputValidationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='TestPass123!'
        )
        self.client = Client()
        self.client.login(username='testuser', password='TestPass123!')

    def test_search_xss_attempt(self):
        response = self.client.get(
            reverse('objects:api_search'),
            {'q': '<script>alert(1)</script>'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b'<script>', response.content)

    def test_markers_invalid_ids(self):
        response = self.client.get(
            reverse('objects:api_markers'),
            {'country': "1; DROP TABLE objects_object;--"},
        )
        self.assertEqual(response.status_code, 200)

    def test_markers_empty_params(self):
        response = self.client.get(
            reverse('objects:api_markers'),
            {'country': '', 'gov_org': ''},
        )
        self.assertEqual(response.status_code, 200)

    def test_search_very_long_query(self):
        response = self.client.get(
            reverse('objects:api_search'),
            {'q': 'А' * 10000},
        )
        self.assertEqual(response.status_code, 200)

    def test_filters_invalid_country(self):
        response = self.client.get(
            reverse('objects:api_filters'),
            {'country': 'not_a_number'},
        )
        self.assertEqual(response.status_code, 200)
