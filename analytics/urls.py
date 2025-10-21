from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # API endpoints for analytics data
    path('api/dashboard-stats/', views.api_dashboard_stats, name='api_dashboard_stats'),
    path('api/summary/', views.analytics_summary_json, name='analytics_summary_json'),
]
