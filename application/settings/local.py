from .defaults import *
import os


DEBUG = True
ALLOWED_HOSTS = ['*', 'localhost', '127.0.0']


STATIC_ROOT = os.getenv('DJANGO_STATIC_ROOT', BASE_DIR / 'static')
MEDIA_ROOT = os.getenv('DJANGO_MEDIA_ROOT', BASE_DIR / 'media')