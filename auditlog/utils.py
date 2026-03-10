from auditlog.middleware import get_current_request
from auditlog.models import AuditLog


def _get_client_ip(request):
    if request is None:
        return None
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def log_action(request, action, details=''):
    """Логирует действие пользователя (поиск, просмотр, фильтрация)."""
    if request is None:
        request = get_current_request()
    user = request.user if request and hasattr(request, 'user') and request.user.is_authenticated else None
    AuditLog.objects.create(
        user=user,
        action=action,
        details=details[:1000],
        ip_address=_get_client_ip(request),
    )
