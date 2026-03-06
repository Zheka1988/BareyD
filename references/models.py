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
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Страна", related_name="gov_orgs")
    name = models.CharField("Название", max_length=200)
    description = models.TextField("Описание", blank=True, null=True)

    class Meta:
        verbose_name = "Гос. орган"
        verbose_name_plural = "Гос. органы"
        ordering = ["name"]

    def __str__(self):
        return self.name


class ForceType(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Страна", related_name="force_types")
    name = models.CharField("Название", max_length=200)
    description = models.TextField("Описание", blank=True, null=True)

    class Meta:
        verbose_name = "Тип сил"
        verbose_name_plural = "Типы сил"
        ordering = ["name"]

    def __str__(self):
        return self.name


class ForceKind(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Страна", related_name="force_kinds")
    name = models.CharField("Название", max_length=200)
    description = models.TextField("Описание", blank=True, null=True)

    class Meta:
        verbose_name = "Вид сил"
        verbose_name_plural = "Виды сил"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Association(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Страна", related_name="associations")
    name = models.CharField("Название", max_length=200)
    description = models.TextField("Описание", blank=True, null=True)

    class Meta:
        verbose_name = "Ассоциация"
        verbose_name_plural = "Ассоциации"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Unit(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Страна", related_name="units")
    name = models.CharField("Название", max_length=200)
    description = models.TextField("Описание", blank=True, null=True)

    class Meta:
        verbose_name = "Часть"
        verbose_name_plural = "Части"
        ordering = ["name"]

    def __str__(self):
        return self.name
