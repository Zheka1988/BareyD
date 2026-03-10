from django.test import TestCase, Client
from django.urls import reverse

from auditlog.models import AuditLog
from users.models import User


class LoginTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='TestPass123!'
        )
        self.login_url = reverse('login')

    def test_login_page_loads(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)

    def test_login_success(self):
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'TestPass123!',
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('objects:map'))

    def test_login_wrong_password(self):
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'wrong',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')

    def test_login_nonexistent_user(self):
        response = self.client.post(self.login_url, {
            'username': 'nobody',
            'password': 'whatever',
        })
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.post(reverse('logout'))
        self.assertIn(response.status_code, [200, 302])

    def test_login_audit_log(self):
        self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'TestPass123!',
        })
        log = AuditLog.objects.filter(action=AuditLog.Action.LOGIN).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.user, self.user)

    def test_logout_audit_log(self):
        self.client.login(username='testuser', password='TestPass123!')
        self.client.post(reverse('logout'))
        log = AuditLog.objects.filter(action=AuditLog.Action.LOGOUT).first()
        self.assertIsNotNone(log)

    def test_failed_login_audit_log(self):
        self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'wrong',
        })
        log = AuditLog.objects.filter(action=AuditLog.Action.LOGIN_FAILED).first()
        self.assertIsNotNone(log)
        self.assertIn('testuser', log.details)


class AccessControlTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='TestPass123!'
        )

    def test_map_requires_login(self):
        response = self.client.get(reverse('objects:map'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_api_markers_requires_login(self):
        response = self.client.get(reverse('objects:api_markers'))
        self.assertEqual(response.status_code, 302)

    def test_api_search_requires_login(self):
        response = self.client.get(reverse('objects:api_search'))
        self.assertEqual(response.status_code, 302)

    def test_api_filters_requires_login(self):
        response = self.client.get(reverse('objects:api_filters'))
        self.assertEqual(response.status_code, 302)

    def test_api_log_export_requires_login(self):
        response = self.client.get(reverse('objects:api_log_export'))
        self.assertEqual(response.status_code, 302)

    def test_authenticated_access(self):
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.get(reverse('objects:map'))
        self.assertEqual(response.status_code, 200)
