from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1')

SERVER_IP = os.getenv('SERVER_IP', '127.0.0.1')
DOMAIN_NAME = os.getenv('DOMAIN_NAME', 'localhost')

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
if SERVER_IP not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(SERVER_IP)
if DOMAIN_NAME not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(DOMAIN_NAME)

CORS_ALLOWED_ORIGINS = [
    'http://localhost',
    'http://127.0.0.1',
    'https://localhost',
    'https://127.0.0.1',
]
if SERVER_IP not in ('127.0.0.1', 'localhost'):
    CORS_ALLOWED_ORIGINS += [f'http://{SERVER_IP}', f'https://{SERVER_IP}']
if DOMAIN_NAME not in ('127.0.0.1', 'localhost'):
    CORS_ALLOWED_ORIGINS += [f'http://{DOMAIN_NAME}', f'https://{DOMAIN_NAME}']

CSRF_TRUSTED_ORIGINS = [
    'http://localhost',
    'http://127.0.0.1',
    'https://localhost',
    'https://127.0.0.1',
]
if SERVER_IP not in ('127.0.0.1', 'localhost'):
    CSRF_TRUSTED_ORIGINS += [f'http://{SERVER_IP}', f'https://{SERVER_IP}']
if DOMAIN_NAME not in ('127.0.0.1', 'localhost'):
    CSRF_TRUSTED_ORIGINS += [f'http://{DOMAIN_NAME}', f'https://{DOMAIN_NAME}']

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 3600
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://redis:6379/0'),
    }
}

RATELIMIT_VIEW = 'BareyD.views.ratelimited'

INSTALLED_APPS = [
    'dal',
    'dal_select2',
    'django.contrib.gis',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'leaflet',
    'djgeojson',
    'references',
    'objects',
    'users',
    'auditlog',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'auditlog.middleware.AuditLogMiddleware',
]

ROOT_URLCONF = 'BareyD.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'BareyD.wsgi.application'

DATABASES = {
    "default": {
        "ENGINE": os.getenv('DB_ENGINE'),
        "NAME": os.getenv('POSTGRES_DB'),
        "USER": os.getenv('POSTGRES_USER'),
        "PASSWORD": os.getenv('POSTGRES_PASSWORD'),
        "HOST": os.getenv('DB_HOST'),
        "PORT": os.getenv('DB_PORT'),
    } #,
    # 'old_sqlite': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': BASE_DIR / 'RFBel.db',
    # }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LEAFLET_CONFIG = {
    'DEFAULT_CENTER': (50.0, 30.0),
    'DEFAULT_ZOOM': 10,
    'MIN_ZOOM': 3,
    'MAX_ZOOM': 18,
    'SCALE': 'both',
    'ATTRIBUTION_PREFIX': 'Мои карты',
}


AUTH_USER_MODEL = 'users.User'

LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

GDAL_LIBRARY_PATH = os.getenv('GDAL_LIBRARY_PATH', '')
GEOS_LIBRARY_PATH = os.getenv('GEOS_LIBRARY_PATH', '')

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/objects/'
LOGOUT_REDIRECT_URL = '/login/'
