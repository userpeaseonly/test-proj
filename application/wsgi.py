import os

from dotenv import load_dotenv

load_dotenv()

from django.core.wsgi import get_wsgi_application

if os.environ.get('DJANGO_ENV') == 'production':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'application.settings.production')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'application.settings.local')

application = get_wsgi_application()
