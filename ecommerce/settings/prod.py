from .base import *
from decouple import config, Csv
import dj_database_url
from datetime import timedelta

DEBUG = False

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

DATABASES = {
    'default': dj_database_url.config(default=config('DATABASE_URL'))
}

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')


CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', cast=Csv())

SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'] = timedelta(minutes=5)