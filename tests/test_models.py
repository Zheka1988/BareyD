from django.contrib.gis.geos import Point, Polygon
from django.core.exceptions import ValidationError
from django.test import TestCase

from objects.models import Object
from references.models import (
    Country, GovOrg, ForceType, ForceKind, Association, Unit,
)


class ObjectModelTest(TestCase):
    def setUp(self):
        self.country = Country.objects.create(name='Тестовая страна')
        self.country2 = Country.objects.create(name='Другая страна')
        self.gov_org = GovOrg.objects.create(name='Орган', country=self.country)
        self.force_type = ForceType.objects.create(name='Тип', country=self.country)
        self.force_kind = ForceKind.objects.create(name='Вид', country=self.country)
        self.association = Association.objects.create(name='Ассоциация', country=self.country)
        self.unit = Unit.objects.create(name='Часть', country=self.country)

    def test_create_object_with_coordinates(self):
        obj = Object.objects.create(
            name='Тестовый объект',
            country=self.country,
            latitude=50.0,
            longitude=30.0,
        )
        self.assertEqual(str(obj), 'Тестовый объект')
        self.assertEqual(obj.latitude, 50.0)

    def test_create_object_with_point(self):
        obj = Object.objects.create(
            name='Объект с точкой',
            country=self.country,
            point=Point(30.0, 50.0, srid=4326),
        )
        self.assertIsNotNone(obj.point)

    def test_create_object_with_polygon(self):
        poly = Polygon(
            ((30, 50), (31, 50), (31, 51), (30, 51), (30, 50)),
            srid=4326,
        )
        obj = Object.objects.create(
            name='Объект с полигоном',
            country=self.country,
            geom=poly,
        )
        self.assertIsNotNone(obj.geom)

    def test_no_geometry_fails(self):
        with self.assertRaises(ValidationError):
            Object.objects.create(
                name='Без геометрии',
                country=self.country,
            )

    def test_multiple_geometry_fails(self):
        with self.assertRaises(ValidationError):
            Object.objects.create(
                name='Две геометрии',
                country=self.country,
                latitude=50.0,
                longitude=30.0,
                point=Point(30.0, 50.0, srid=4326),
            )

    def test_latitude_without_longitude_fails(self):
        with self.assertRaises(ValidationError):
            Object.objects.create(
                name='Только широта',
                country=self.country,
                latitude=50.0,
            )

    def test_country_mismatch_fails(self):
        gov_org_other = GovOrg.objects.create(name='Чужой орган', country=self.country2)
        with self.assertRaises(ValidationError):
            Object.objects.create(
                name='Несовпадение стран',
                country=self.country,
                gov_org=gov_org_other,
                latitude=50.0,
                longitude=30.0,
            )

    def test_all_references_same_country(self):
        obj = Object.objects.create(
            name='Все справочники',
            country=self.country,
            gov_org=self.gov_org,
            type=self.force_type,
            kind=self.force_kind,
            association=self.association,
            unit=self.unit,
            latitude=50.0,
            longitude=30.0,
        )
        self.assertEqual(obj.country, self.country)

    def test_object_without_name_fails(self):
        with self.assertRaises(ValidationError):
            Object.objects.create(
                name='',
                country=self.country,
                latitude=50.0,
                longitude=30.0,
            )

    def test_str_fallback_to_short_name(self):
        obj = Object.objects.create(
            name='Основное',
            short_name='Короткое',
            country=self.country,
            latitude=50.0,
            longitude=30.0,
        )
        self.assertIn('Основное', str(obj))


class ReferenceModelTest(TestCase):
    def setUp(self):
        self.country = Country.objects.create(name='Страна')

    def test_country_str(self):
        self.assertEqual(str(self.country), 'Страна')

    def test_gov_org_with_country(self):
        org = GovOrg.objects.create(name='Орган', country=self.country)
        self.assertEqual(org.country, self.country)

    def test_gov_org_without_country(self):
        org = GovOrg.objects.create(name='Общий орган')
        self.assertIsNone(org.country)

    def test_reference_ordering(self):
        Country.objects.create(name='Б')
        Country.objects.create(name='А')
        names = list(Country.objects.values_list('name', flat=True))
        self.assertEqual(names, sorted(names))

    def test_cascade_delete_country(self):
        org = GovOrg.objects.create(name='Орган', country=self.country)
        self.country.delete()
        self.assertFalse(GovOrg.objects.filter(pk=org.pk).exists())
