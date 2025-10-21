from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    # Basic CRUD operations
    path('', views.TaskListCreateView.as_view(), name='task-list-create'),
    path('<int:pk>/', views.TaskRetrieveUpdateDestroyView.as_view(), name='task-detail'),
    
    # Task status operations
    path('<int:pk>/complete/', views.mark_task_completed, name='mark-task-completed'),
    path('<int:pk>/pending/', views.mark_task_pending, name='mark-task-pending'),
    path('<int:pk>/toggle/', views.toggle_task_completion, name='toggle-task-completion'),
    
    # Statistics
    path('stats/', views.task_stats, name='task-stats'),
]