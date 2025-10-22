from .defaults import *
import os


DEBUG = int(os.getenv('DEBUG'))
print("Type of DEBUG:", type(DEBUG))
print("Production DEBUG:", bool(DEBUG))

ALLOWED_HOSTS = ['*', 'localhost', '127.0.0']


STATIC_ROOT = os.getenv('DJANGO_STATIC_ROOT', BASE_DIR / 'static')
MEDIA_ROOT = os.getenv('DJANGO_MEDIA_ROOT', BASE_DIR / 'media')