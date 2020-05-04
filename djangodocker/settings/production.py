from os import environ, getenv
from .base import *
import django_heroku
import dj_database_url

# This line should already exist in your settings.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = environ["SECRET_KEY"],

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = [
    environ["ALLOWED_HOST"],'.herokuapp.com',
]

django_heroku.settings(locals())
DATABASES = {}
DATABASES['default'] = dj_database_url.config(conn_max_age=500)
# Logging

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
             'level': getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
        },
    },
}
