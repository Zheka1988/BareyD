"""Настройки для тестов — отключает SSL-редирект и rate limiting."""
from BareyD.settings import *  # noqa: F401,F403

SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

RATELIMIT_ENABLE = False

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
