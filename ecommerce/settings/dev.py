from .base import *
from decouple import config, Csv
from datetime import timedelta
DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', cast=Csv())

SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'] = timedelta(days=1)

TIME_ZONE = 'Africa/Cairo'

BASE_URL = "http://127.0.0.1:8000"