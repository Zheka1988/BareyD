import json

from django.contrib.gis.geos import Point, Polygon
from django.test import TestCase, Client
from django.urls import reverse

from auditlog.models import AuditLog
from objects.models import Object
from references.models import (
    Country, GovOrg, ForceType, ForceKind, Association, Unit,
)
from users.models import User


class ApiTestBase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='TestPass123!'
        )
        self.client.login(username='testuser', password='TestPass123!')
        AuditLog.objects.all().delete()

        self.country = Country.objects.create(name='Страна')
        self.country2 = Country.objects.create(name='Другая')
        self.gov_org = GovOrg.objects.create(name='Орган', country=self.country)
        self.force_type = ForceType.objects.create(name='Тип', country=self.country)

        self.obj1 = Object.objects.create(
            name='Объект Альфа',
            country=self.country,
            gov_org=self.gov_org,
            type=self.force_type,
            latitude=50.0,
            longitude=30.0,
        )
        self.obj2 = Object.objects.create(
            name='Объект Бета',
            country=self.country2,
            latitude=55.0,
            longitude=35.0,
        )
        self.obj_poly = Object.objects.create(
            name='Объект Полигон',
            country=self.country,
            geom=Polygon(
                ((30, 50), (31, 50), (31, 51), (30, 51), (30, 50)),
                srid=4326,
            ),
        )


class ApiMarkersTest(ApiTestBase):
    def test_no_filters_returns_empty(self):
        response = self.client.get(reverse('objects:api_markers'))
        data = json.loads(response.content)
        self.assertEqual(data['objects'], [])
        self.assertEqual(data['total'], 3)

    def test_filter_by_country(self):
        response = self.client.get(
            reverse('objects:api_markers'),
            {'country': str(self.country.pk)},
        )
        data = json.loads(response.content)
        names = [o['name'] for o in data['objects']]
        self.assertIn('Объект Альфа', names)
        self.assertIn('Объект Полигон', names)
        self.assertNotIn('Объект Бета', names)

    def test_filter_by_multiple_params(self):
        response = self.client.get(
            reverse('objects:api_markers'),
            {'country': str(self.country.pk), 'gov_org': str(self.gov_org.pk)},
        )
        data = json.loads(response.content)
        self.assertEqual(len(data['objects']), 1)
        self.assertEqual(data['objects'][0]['name'], 'Объект Альфа')

    def test_serialization_coordinates(self):
        response = self.client.get(
            reverse('objects:api_markers'),
            {'country': str(self.country.pk)},
        )
        data = json.loads(response.content)
        alfa = next(o for o in data['objects'] if o['name'] == 'Объект Альфа')
        self.assertEqual(alfa['lat'], 50.0)
        self.assertEqual(alfa['lng'], 30.0)
        self.assertIsNone(alfa['geom'])

    def test_serialization_polygon(self):
        response = self.client.get(
            reverse('objects:api_markers'),
            {'country': str(self.country.pk)},
        )
        data = json.loads(response.content)
        poly = next(o for o in data['objects'] if o['name'] == 'Объект Полигон')
        self.assertIsNone(poly['lat'])
        self.assertIsNotNone(poly['geom'])

    def test_filter_logs_audit(self):
        self.client.get(
            reverse('objects:api_markers'),
            {'country': str(self.country.pk)},
        )
        log = AuditLog.objects.filter(action=AuditLog.Action.FILTER).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.user, self.user)

    def test_invalid_filter_ids_ignored(self):
        response = self.client.get(
            reverse('objects:api_markers'),
            {'country': 'abc,!@#'},
        )
        data = json.loads(response.content)
        self.assertEqual(data['objects'], [])


class ApiSearchTest(ApiTestBase):
    def test_search_finds_object(self):
        response = self.client.get(
            reverse('objects:api_search'), {'q': 'Альфа'},
        )
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'Объект Альфа')

    def test_search_case_insensitive(self):
        response = self.client.get(
            reverse('objects:api_search'), {'q': 'альфа'},
        )
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)

    def test_search_partial_match(self):
        response = self.client.get(
            reverse('objects:api_search'), {'q': 'Объект'},
        )
        data = json.loads(response.content)
        self.assertEqual(len(data), 3)

    def test_search_min_length(self):
        response = self.client.get(
            reverse('objects:api_search'), {'q': 'А'},
        )
        data = json.loads(response.content)
        self.assertEqual(data, [])

    def test_search_empty_query(self):
        response = self.client.get(
            reverse('objects:api_search'), {'q': ''},
        )
        data = json.loads(response.content)
        self.assertEqual(data, [])

    def test_search_no_results(self):
        response = self.client.get(
            reverse('objects:api_search'), {'q': 'Несуществующий'},
        )
        data = json.loads(response.content)
        self.assertEqual(len(data), 0)

    def test_search_max_20_results(self):
        for i in range(25):
            Object.objects.create(
                name=f'Тестовый {i}',
                country=self.country,
                latitude=50.0 + i * 0.01,
                longitude=30.0,
            )
        response = self.client.get(
            reverse('objects:api_search'), {'q': 'Тестовый'},
        )
        data = json.loads(response.content)
        self.assertLessEqual(len(data), 20)

    def test_search_long_query_truncated(self):
        long_query = 'А' * 200
        response = self.client.get(
            reverse('objects:api_search'), {'q': long_query},
        )
        self.assertEqual(response.status_code, 200)

    def test_search_logs_audit(self):
        self.client.get(
            reverse('objects:api_search'), {'q': 'Альфа'},
        )
        log = AuditLog.objects.filter(action=AuditLog.Action.SEARCH).first()
        self.assertIsNotNone(log)
        self.assertIn('Альфа', log.details)


class ApiFiltersTest(ApiTestBase):
    def test_filters_returns_all(self):
        response = self.client.get(reverse('objects:api_filters'))
        data = json.loads(response.content)
        self.assertIn('country', data)
        self.assertIn('gov_org', data)
        self.assertIn('type', data)
        self.assertIn('kind', data)
        self.assertIn('association', data)
        self.assertIn('unit', data)

    def test_filters_country_has_items(self):
        response = self.client.get(reverse('objects:api_filters'))
        data = json.loads(response.content)
        country_names = [c['name'] for c in data['country']]
        self.assertIn('Страна', country_names)
        self.assertIn('Другая', country_names)

    def test_filters_by_country(self):
        response = self.client.get(
            reverse('objects:api_filters'),
            {'country': str(self.country.pk)},
        )
        data = json.loads(response.content)
        gov_org_names = [g['name'] for g in data['gov_org']]
        self.assertIn('Орган', gov_org_names)

    def test_filters_format(self):
        response = self.client.get(reverse('objects:api_filters'))
        data = json.loads(response.content)
        for item in data['country']:
            self.assertIn('id', item)
            self.assertIn('name', item)


class ApiLogExportTest(ApiTestBase):
    def test_log_export(self):
        response = self.client.get(
            reverse('objects:api_log_export'),
            {'format': 'csv', 'count': '10'},
        )
        data = json.loads(response.content)
        self.assertTrue(data['ok'])

    def test_log_export_audit(self):
        self.client.get(
            reverse('objects:api_log_export'),
            {'format': 'xlsx', 'count': '5'},
        )
        log = AuditLog.objects.filter(action=AuditLog.Action.EXPORT).first()
        self.assertIsNotNone(log)
        self.assertIn('xlsx', log.details)
        self.assertIn('5', log.details)
