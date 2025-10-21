from django.apps import AppConfig


class ApplicationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'application'
    
    def ready(self):
        # Import admin configuration after apps are loaded
        from . import admin