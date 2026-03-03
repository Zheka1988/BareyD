from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Модель расширяющая, пользователя по умолчанию"""

    def __str__(self):
        full = self.get_full_name().strip()
        return full or self.username

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
