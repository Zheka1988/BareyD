from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from auditlog.models import AuditLog


class Command(BaseCommand):
    help = 'Удаляет записи аудита старше 3 месяцев'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days', type=int, default=90,
            help='Количество дней хранения (по умолчанию 90)',
        )

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(days=options['days'])
        count, _ = AuditLog.objects.filter(timestamp__lt=cutoff).delete()
        self.stdout.write(f'Удалено {count} записей старше {cutoff:%d.%m.%Y}')
