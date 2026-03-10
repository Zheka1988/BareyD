from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    class Action(models.TextChoices):
        CREATE = 'create', 'Создание'
        UPDATE = 'update', 'Редактирование'
        DELETE = 'delete', 'Удаление'
        LOGIN = 'login', 'Вход'
        LOGOUT = 'logout', 'Выход'
        LOGIN_FAILED = 'login_failed', 'Неудачный вход'
        SEARCH = 'search', 'Поиск'
        VIEW = 'view', 'Просмотр'
        FILTER = 'filter', 'Фильтрация'
        EXPORT = 'export', 'Экспорт'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name='Пользователь',
    )
    action = models.CharField('Действие', max_length=20, choices=Action.choices)
    model_name = models.CharField('Модель', max_length=100, blank=True, default='')
    object_id = models.CharField('ID объекта', max_length=50, blank=True, default='')
    object_repr = models.CharField('Представление', max_length=255, blank=True, default='')
    details = models.TextField('Детали', blank=True, default='')
    ip_address = models.GenericIPAddressField('IP-адрес', null=True, blank=True)
    timestamp = models.DateTimeField('Дата/время', auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Запись аудита'
        verbose_name_plural = 'Журнал аудита'
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
            models.Index(fields=['model_name', '-timestamp']),
        ]

    def __str__(self):
        user = self.user or 'Аноним'
        return f'[{self.timestamp:%d.%m.%Y %H:%M}] {user} — {self.get_action_display()}'
