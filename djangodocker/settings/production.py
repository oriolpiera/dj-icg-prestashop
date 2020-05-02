from os import environ
from .base import *
import django_heroku
import dj_database_url

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = environ["SECRET_KEY"],

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = [
    environ["ALLOWED_HOST"],'.herokuapp.com',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'USER': 'oriol',
        'NAME': 'django',
    },
}

django_heroku.settings(locals())
db_from_env = dj_database_url.config(conn_max_age=500)
DATABASES['default'].update(db_from_env)
