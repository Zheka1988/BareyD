from django.contrib.gis.db import models
from django.core.exceptions import ValidationError
from references.models import Country, GovOrg, ForceType, ForceKind, Association, Unit


class Object(models.Model):
    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="obj_country",
        verbose_name="Страна",
    )
    gov_org = models.ForeignKey(
        GovOrg,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="obj_gov_org",
        verbose_name="Гос. орган",
    )
    type = models.ForeignKey(
        ForceType,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="obj_type",
        verbose_name="Тип сил",
    )
    kind = models.ForeignKey(
        ForceKind,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="obj_kind",
        verbose_name="Вид сил",
    )
    association = models.ForeignKey(
        Association,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="obj_association",
        verbose_name="Ассоциация",
    )
    unit = models.ForeignKey(
        Unit,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="obj_unit",
        verbose_name="Часть",
    )

    name = models.CharField("Название", max_length=300)
    short_name = models.CharField("Краткое название", max_length=100, blank=True, null=True)

    latitude = models.FloatField(
        "Широта",
        null=True,
        blank=True,
    )
    longitude = models.FloatField(
        "Долгота",
        null=True,
        blank=True,
    )

    description = models.TextField("Описание", blank=True, null=True)

    picture = models.ImageField('Изображение', blank=True, null=True)

    geom = models.PolygonField(
        verbose_name="Полигон",
        srid=4326,
        null=True,
        blank=True,
        geography=False
    )

    point = models.PointField(
        verbose_name="Точка на карте",
        srid=4326,
        null=True,
        blank=True,
        geography=False
    )

    class Meta:
        verbose_name = "Объект"
        verbose_name_plural = "Объекты"
        ordering = ["name"]

    def clean(self):
        has_latlon = self.latitude is not None and self.longitude is not None
        has_point = self.point is not None
        has_geom = self.geom is not None
        filled = sum([has_latlon, has_point, has_geom])

        if filled == 0:
            raise ValidationError(
                "Укажите геометрию: координаты (широта/долгота), точку на карте или полигон."
            )

        if filled > 1:
            raise ValidationError(
                "Можно задать только один вариант геометрии: "
                "полигон, точку на карте или координаты (широта/долгота)."
            )

        if (self.latitude is None) != (self.longitude is None):
            raise ValidationError(
                "Широта и долгота должны быть заполнены вместе."
            )

        if self.country_id:
            ref_fields = [
                ('gov_org', 'Гос. орган'),
                ('type', 'Тип сил'),
                ('kind', 'Вид сил'),
                ('association', 'Ассоциация'),
                ('unit', 'Часть'),
            ]
            for field, label in ref_fields:
                ref = getattr(self, field)
                if ref and ref.country_id and ref.country_id != self.country_id:
                    raise ValidationError(
                        f'{label} «{ref}» относится к другой стране.'
                    )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name or self.short_name or f"Object #{self.pk}"

    @property
    def picture_url(self):
        return self.picture.url
