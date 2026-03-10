from django.test import TestCase, Client
from django.urls import reverse

from auditlog.models import AuditLog
from objects.models import Object
from references.models import Country, GovOrg
from users.models import User


class AuditCrudTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='TestPass123!'
        )
        self.client = Client()
        self.client.login(username='testuser', password='TestPass123!')
        AuditLog.objects.all().delete()

    def test_create_object_logged(self):
        country = Country.objects.create(name='Страна')
        AuditLog.objects.all().delete()

        Object.objects.create(
            name='Новый', country=country, latitude=50.0, longitude=30.0,
        )
        log = AuditLog.objects.filter(
            action=AuditLog.Action.CREATE,
            model_name='objects.Object',
        ).first()
        self.assertIsNotNone(log)
        self.assertIn('Новый', log.object_repr)

    def test_update_object_logged(self):
        country = Country.objects.create(name='Страна')
        obj = Object.objects.create(
            name='Старое', country=country, latitude=50.0, longitude=30.0,
        )
        AuditLog.objects.all().delete()

        obj.name = 'Обновлённое'
        obj.save()
        log = AuditLog.objects.filter(
            action=AuditLog.Action.UPDATE,
            model_name='objects.Object',
        ).first()
        self.assertIsNotNone(log)

    def test_delete_object_logged(self):
        country = Country.objects.create(name='Страна')
        obj = Object.objects.create(
            name='Удаляемый', country=country, latitude=50.0, longitude=30.0,
        )
        AuditLog.objects.all().delete()

        obj.delete()
        log = AuditLog.objects.filter(
            action=AuditLog.Action.DELETE,
            model_name='objects.Object',
        ).first()
        self.assertIsNotNone(log)
        self.assertIn('Удаляемый', log.object_repr)

    def test_create_reference_logged(self):
        AuditLog.objects.all().delete()
        Country.objects.create(name='Новая страна')
        log = AuditLog.objects.filter(
            action=AuditLog.Action.CREATE,
            model_name='references.Country',
        ).first()
        self.assertIsNotNone(log)

    def test_create_user_logged(self):
        AuditLog.objects.all().delete()
        User.objects.create_user(username='newuser', password='Pass123!')
        log = AuditLog.objects.filter(
            action=AuditLog.Action.CREATE,
            model_name='users.User',
        ).first()
        self.assertIsNotNone(log)

    def test_last_login_not_logged(self):
        """Обновление last_login при входе не должно создавать запись UPDATE."""
        AuditLog.objects.all().delete()
        self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'TestPass123!',
        })
        update_logs = AuditLog.objects.filter(
            action=AuditLog.Action.UPDATE,
            model_name='users.User',
        )
        self.assertEqual(update_logs.count(), 0)

    def test_view_map_logged(self):
        AuditLog.objects.all().delete()
        self.client.get(reverse('objects:map'))
        log = AuditLog.objects.filter(action=AuditLog.Action.VIEW).first()
        self.assertIsNotNone(log)
        self.assertIn('карты', log.details.lower())


class AuditCleanupTest(TestCase):
    def test_clean_old_logs_command(self):
        from datetime import timedelta
        from django.utils import timezone
        from django.core.management import call_command

        old_log = AuditLog.objects.create(
            action=AuditLog.Action.VIEW,
            details='Старая запись',
        )
        AuditLog.objects.filter(pk=old_log.pk).update(
            timestamp=timezone.now() - timedelta(days=100),
        )
        fresh_log = AuditLog.objects.create(
            action=AuditLog.Action.VIEW,
            details='Свежая запись',
        )

        call_command('clean_old_logs', '--days=90')

        self.assertFalse(AuditLog.objects.filter(pk=old_log.pk).exists())
        self.assertTrue(AuditLog.objects.filter(pk=fresh_log.pk).exists())
