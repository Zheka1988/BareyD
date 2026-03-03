from django.db import models


class Country(models.Model):
    name = models.CharField("Название", max_length=200)

    class Meta:
        verbose_name = "Страна"
        verbose_name_plural = "Страны"
        ordering = ["name"]

    def __str__(self):
        return self.name


class GovOrg(models.Model):
    name = models.CharField("Название", max_length=200)
    description = models.TextField("Описание", blank=True, null=True)

    class Meta:
        verbose_name = "Гос. орган"
        verbose_name_plural = "Гос. органы"
        ordering = ["name"]

    def __str__(self):
        return self.name


class ForceType(models.Model):
    name = models.CharField("Название", max_length=200)
    description = models.TextField("Описание", blank=True, null=True)

    class Meta:
        verbose_name = "Тип сил"
        verbose_name_plural = "Типы сил"
        ordering = ["name"]

    def __str__(self):
        return self.name


class ForceKind(models.Model):
    name = models.CharField("Название", max_length=200)
    description = models.TextField("Описание", blank=True, null=True)

    class Meta:
        verbose_name = "Вид сил"
        verbose_name_plural = "Виды сил"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Association(models.Model):
    name = models.CharField("Название", max_length=200)
    description = models.TextField("Описание", blank=True, null=True)

    class Meta:
        verbose_name = "Ассоциация"
        verbose_name_plural = "Ассоциации"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Unit(models.Model):
    name = models.CharField("Название", max_length=200)
    description = models.TextField("Описание", blank=True, null=True)

    class Meta:
        verbose_name = "Часть"
        verbose_name_plural = "Части"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Polygon(models.Model):
    name = models.CharField("Название", max_length=200)
    color = models.CharField("Цвет", max_length=50, blank=True, null=True)  # hex или название цвета

    class Meta:
        verbose_name = "Полигон"
        verbose_name_plural = "Полигоны"
        ordering = ["name"]

    def __str__(self):
        return self.name


class PolygonPoint(models.Model):
    polygon = models.ForeignKey(
        Polygon,
        on_delete=models.CASCADE,
        related_name="points",
        verbose_name="Полигон",
    )
    lat = models.FloatField("Широта")
    lng = models.FloatField("Долгота")

    class Meta:
        verbose_name = "Точка полигона"
        verbose_name_plural = "Точки полигона"
        ordering = ["polygon", "id"]

    def __str__(self):
        return f"Точка полигона {self.polygon.name}"


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

    latitude = models.FloatField("Широта")
    longitude = models.FloatField("Долгота")

    description = models.TextField("Описание", blank=True, null=True)

    class Meta:
        verbose_name = "Объект"
        verbose_name_plural = "Объекты"
        ordering = ["name"]

    def __str__(self):
        return self.name