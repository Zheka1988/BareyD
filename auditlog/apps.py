from django.apps import AppConfig


class AuditlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'auditlog'
    verbose_name = 'Журнал аудита'

    def ready(self):
        import auditlog.signals  # noqa: F401
