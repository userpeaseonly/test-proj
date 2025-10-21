import os

from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include
from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from analytics.admin import analytics_admin_site

# Import the restricted admin
from application.admin import restricted_admin_site

urlpatterns = [
    path('admin/', restricted_admin_site.urls),  # Use restricted admin
    path('analytics-admin/', analytics_admin_site.urls),
    path('analytics/', include('analytics.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/auth/', include('users.urls')),
    path('api/tasks/', include('tasks.urls')),

]

urlpatterns += i18n_patterns(

)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
