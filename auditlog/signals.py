from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from auditlog.middleware import get_current_request
from auditlog.models import AuditLog

TRACKED_MODELS = {
    'objects.Object',
    'references.Country',
    'references.GovOrg',
    'references.ForceType',
    'references.ForceKind',
    'references.Association',
    'references.Unit',
    'users.User',
    'auth.Group',
    'auth.Permission',
}


def _get_client_ip(request):
    if request is None:
        return None
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def _get_model_label(instance):
    return f'{instance._meta.app_label}.{instance._meta.object_name}'


# ── CRUD ──

@receiver(post_save)
def on_model_save(sender, instance, created, **kwargs):
    label = _get_model_label(instance)
    if label not in TRACKED_MODELS:
        return
    if label == 'auditlog.AuditLog':
        return

    update_fields = kwargs.get('update_fields')
    if update_fields and set(update_fields) <= {'last_login'}:
        return

    request = get_current_request()
    action = AuditLog.Action.CREATE if created else AuditLog.Action.UPDATE
    AuditLog.objects.create(
        user=getattr(request, 'user', None) if request and hasattr(request, 'user') and request.user.is_authenticated else None,
        action=action,
        model_name=label,
        object_id=str(instance.pk),
        object_repr=str(instance)[:255],
        ip_address=_get_client_ip(request),
    )


@receiver(post_delete)
def on_model_delete(sender, instance, **kwargs):
    label = _get_model_label(instance)
    if label not in TRACKED_MODELS:
        return

    request = get_current_request()
    AuditLog.objects.create(
        user=getattr(request, 'user', None) if request and hasattr(request, 'user') and request.user.is_authenticated else None,
        action=AuditLog.Action.DELETE,
        model_name=label,
        object_id=str(instance.pk),
        object_repr=str(instance)[:255],
        ip_address=_get_client_ip(request),
    )


# ── Аутентификация ──

@receiver(user_logged_in)
def on_login(sender, request, user, **kwargs):
    AuditLog.objects.create(
        user=user,
        action=AuditLog.Action.LOGIN,
        model_name='users.User',
        object_id=str(user.pk),
        object_repr=str(user)[:255],
        ip_address=_get_client_ip(request),
    )


@receiver(user_logged_out)
def on_logout(sender, request, user, **kwargs):
    AuditLog.objects.create(
        user=user,
        action=AuditLog.Action.LOGOUT,
        model_name='users.User',
        object_id=str(user.pk) if user else '',
        object_repr=str(user)[:255] if user else '',
        ip_address=_get_client_ip(request),
    )


@receiver(user_login_failed)
def on_login_failed(sender, credentials, request, **kwargs):
    AuditLog.objects.create(
        user=None,
        action=AuditLog.Action.LOGIN_FAILED,
        details=f"Попытка входа: {credentials.get('username', '?')}",
        ip_address=_get_client_ip(request),
    )
