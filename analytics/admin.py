from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import path, reverse
from django.utils.html import format_html
from django.views.decorators.cache import cache_page
from django.utils import timezone
from datetime import timedelta
from tasks.models import Task

User = get_user_model()


class ReadOnlyAdminMixin:
    """Mixin to make admin interfaces read-only"""
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


class TaskReadOnlyAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    """Read-only admin interface for tasks"""
    list_display = ['title', 'user_email', 'completed', 'created_at', 'updated_at']
    list_filter = ['completed', 'created_at', 'user']
    search_fields = ['title', 'description', 'user__email']
    ordering = ['-created_at']
    readonly_fields = ['title', 'description', 'user', 'completed', 'created_at', 'updated_at']
    
    def user_email(self, obj):
        return obj.user.email if obj.user else 'No User'
    user_email.short_description = 'User Email'


class UserReadOnlyAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    """Read-only admin interface for users"""
    list_display = ['email', 'first_name', 'last_name', 'role', 'task_count', 'completion_rate', 'date_joined']
    list_filter = ['role', 'date_joined']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    readonly_fields = ['email', 'first_name', 'last_name', 'role', 'date_joined', 'last_login']
    
    def get_queryset(self, request):
        """Add task statistics to queryset"""
        return super().get_queryset(request).annotate(
            task_count_annotated=Count('tasks'),
            completed_count=Count('tasks', filter=Q(tasks__completed=True))
        )
    
    def task_count(self, obj):
        return getattr(obj, 'task_count_annotated', 0)
    task_count.short_description = 'Total Tasks'
    task_count.admin_order_field = 'task_count_annotated'
    
    def completion_rate(self, obj):
        total = getattr(obj, 'task_count_annotated', 0)
        completed = getattr(obj, 'completed_count', 0)
        if total > 0:
            rate = (completed / total) * 100
            return f"{rate:.1f}%"
        return "0%"
    completion_rate.short_description = 'Completion Rate'


class AnalyticsAdminSite(AdminSite):
    """Custom admin site for analytics dashboard"""
    site_header = 'Analytics Dashboard'
    site_title = 'Analytics Admin'
    index_title = 'Task & User Analytics'
    
    def get_urls(self):
        """Add custom URLs for analytics views"""
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.dashboard_view), name='analytics_dashboard'),
            path('users/', self.admin_view(self.user_analytics_view), name='analytics_users'),
            path('tasks/', self.admin_view(self.task_analytics_view), name='analytics_tasks'),
        ]
        return custom_urls + urls
    
    def index(self, request, extra_context=None):
        """Custom admin index that redirects to dashboard"""
        return redirect('analytics_admin:analytics_dashboard')
    
    def dashboard_view(self, request):
        """Main analytics dashboard view"""
        
        # Calculate overall statistics using PostgreSQL aggregation
        task_stats = Task.objects.aggregate(
            total_tasks=Count('id'),
            completed_tasks=Count('id', filter=Q(completed=True)),
            pending_tasks=Count('id', filter=Q(completed=False))
        )
        
        user_stats_agg = User.objects.aggregate(
            total_users=Count('id'),
            active_users=Count('id', filter=Q(tasks__isnull=False), distinct=True)
        )
        
        completion_rate = 0
        if task_stats['total_tasks'] > 0:
            completion_rate = (task_stats['completed_tasks'] / task_stats['total_tasks']) * 100
        
        # Get top users by task count using PostgreSQL aggregation
        top_users = User.objects.annotate(
            task_count=Count('tasks'),
            completed_count=Count('tasks', filter=Q(tasks__completed=True))
        ).filter(task_count__gt=0).order_by('-task_count')[:5]
        
        # Add completion rates
        for user in top_users:
            if user.task_count > 0:
                user.completion_rate = (user.completed_count / user.task_count) * 100
            else:
                user.completion_rate = 0
        
        # Get recent activity
        recent_tasks = Task.objects.select_related('user').order_by('-created_at')[:5]
        
        # Get daily stats for the last 7 days
        daily_stats = []
        for i in range(7):
            date = timezone.now().date() - timedelta(days=i)
            day_stats = Task.objects.filter(created_at__date=date).aggregate(
                created_count=Count('id'),
                completed_count=Count('id', filter=Q(completed=True, updated_at__date=date))
            )
            daily_stats.append({
                'date': date.strftime('%Y-%m-%d'),
                'created': day_stats['created_count'] or 0,
                'completed': day_stats['completed_count'] or 0
            })
        
        context = {
            'title': 'Analytics Dashboard',
            'total_tasks': task_stats['total_tasks'],
            'completed_tasks': task_stats['completed_tasks'],
            'pending_tasks': task_stats['pending_tasks'],
            'total_users': user_stats_agg['total_users'],
            'active_users': user_stats_agg['active_users'],
            'completion_rate': round(completion_rate, 2),
            'top_users': top_users,
            'recent_tasks': recent_tasks,
            'daily_stats': list(reversed(daily_stats)),
        }
        
        return render(request, 'admin/analytics/dashboard.html', context)
    
    def user_analytics_view(self, request):
        """User analytics view with detailed statistics"""
        
        users_with_stats = User.objects.annotate(
            task_count=Count('tasks'),
            completed_count=Count('tasks', filter=Q(tasks__completed=True)),
            pending_count=Count('tasks', filter=Q(tasks__completed=False))
        ).order_by('-task_count')
        
        # Add completion rate calculation
        for user in users_with_stats:
            if user.task_count > 0:
                user.completion_rate = round((user.completed_count / user.task_count) * 100, 2)
            else:
                user.completion_rate = 0
        
        context = {
            'title': 'User Analytics',
            'users_with_stats': users_with_stats,
        }
        
        return render(request, 'admin/analytics/users.html', context)
    
    def task_analytics_view(self, request):
        """Task analytics view with comprehensive statistics"""
        
        # Basic task statistics - using different field names to avoid conflicts
        task_stats = Task.objects.aggregate(
            total=Count('id'),
            completed_count=Count('id', filter=Q(completed=True)),
            pending_count=Count('id', filter=Q(completed=False))
        )
        
        # Calculate completion rate
        if task_stats['total'] > 0:
            task_stats['completion_rate'] = round(
                (task_stats['completed_count'] / task_stats['total']) * 100, 2
            )
        else:
            task_stats['completion_rate'] = 0
        
        # Tasks grouped by user - fixed aggregation
        tasks_by_user = User.objects.annotate(
            task_count=Count('tasks'),
            completed_tasks=Count('tasks', filter=Q(tasks__completed=True)),
            pending_tasks=Count('tasks', filter=Q(tasks__completed=False))
        ).filter(task_count__gt=0).order_by('-task_count')
        
        # Add completion rates
        for user in tasks_by_user:
            user.completion_rate = round(
                (user.completed_tasks / user.task_count) * 100, 2
            ) if user.task_count > 0 else 0
        
        # Recent tasks
        recent_tasks = Task.objects.select_related('user').order_by('-created_at')[:20]
        
        context = {
            'title': 'Task Analytics',
            'task_stats': task_stats,
            'tasks_by_user': tasks_by_user,
            'recent_tasks': recent_tasks,
        }
        
        return render(request, 'admin/analytics/tasks.html', context)


# Create the analytics admin site instance
analytics_admin_site = AnalyticsAdminSite(name='analytics_admin')

# Register models with the analytics admin site (read-only)
analytics_admin_site.register(Task, TaskReadOnlyAdmin)
analytics_admin_site.register(User, UserReadOnlyAdmin)
