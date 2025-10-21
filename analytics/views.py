from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.db.models import Count, Q, Avg, Sum, Case, When, F, DurationField
from django.db.models.functions import Extract
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.utils import timezone
from datetime import timedelta
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from tasks.models import Task

User = get_user_model()


@staff_member_required
def analytics_dashboard(request):
    """Main analytics dashboard view using PostgreSQL aggregation"""
    
    # Calculate overall statistics using aggregation
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
    
    # Get user statistics with task counts using PostgreSQL aggregation
    user_stats = User.objects.annotate(
        task_count=Count('tasks'),
        completed_count=Count('tasks', filter=Q(tasks__completed=True)),
        pending_count=Count('tasks', filter=Q(tasks__completed=False))
    ).filter(task_count__gt=0).order_by('-task_count')[:10]
    
    # Calculate completion rates for users
    for user in user_stats:
        if user.task_count > 0:
            user.completion_rate = (user.completed_count / user.task_count) * 100
        else:
            user.completion_rate = 0
    
    # Get recent activity
    recent_tasks = Task.objects.select_related('user').order_by('-created_at')[:10]
    
    # Get daily statistics for the last 7 days using aggregation
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
        'total_tasks': task_stats['total_tasks'],
        'completed_tasks': task_stats['completed_tasks'],
        'pending_tasks': task_stats['pending_tasks'],
        'total_users': user_stats_agg['total_users'],
        'active_users': user_stats_agg['active_users'],
        'completion_rate': round(completion_rate, 2),
        'user_stats': user_stats,
        'recent_tasks': recent_tasks,
        'daily_stats': list(reversed(daily_stats)),  # Show oldest to newest
    }
    
    return render(request, 'admin/analytics/dashboard.html', context)


@staff_member_required
def user_analytics(request):
    """User analytics view with detailed statistics using PostgreSQL aggregation"""
    
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
        'users_with_stats': users_with_stats,
    }
    
    return render(request, 'admin/analytics/user_analytics.html', context)


@staff_member_required
def task_analytics(request):
    """Task analytics view with comprehensive task statistics using PostgreSQL aggregation"""
    
    # Basic task statistics using aggregation
    task_stats = Task.objects.aggregate(
        total=Count('id'),
        completed=Count('id', filter=Q(completed=True)),
        pending=Count('id', filter=Q(completed=False))
    )
    
    # Calculate completion rate
    if task_stats['total'] > 0:
        task_stats['completion_rate'] = round(
            (task_stats['completed'] / task_stats['total']) * 100, 2
        )
    else:
        task_stats['completion_rate'] = 0
    
    # Tasks grouped by user using PostgreSQL aggregation
    tasks_by_user = User.objects.annotate(
        task_count=Count('tasks'),
        completed_count=Count('tasks', filter=Q(tasks__completed=True)),
        pending_count=Count('tasks', filter=Q(tasks__completed=False))
    ).filter(task_count__gt=0).order_by('-task_count')
    
    # Add completion rates
    for user in tasks_by_user:
        user.completion_rate = round(
            (user.completed_count / user.task_count) * 100, 2
        ) if user.task_count > 0 else 0
    
    # All tasks with user information (limited for performance)
    all_tasks = Task.objects.select_related('user').order_by('-created_at')[:100]
    
    # Monthly task creation trend using PostgreSQL aggregation
    monthly_stats = []
    for i in range(6):  # Last 6 months
        date = timezone.now().date().replace(day=1) - timedelta(days=30*i)
        month_start = date.replace(day=1)
        
        # Get the end of the month
        if i == 0:
            month_end = timezone.now().date()
        else:
            if month_start.month == 12:
                next_month = month_start.replace(year=month_start.year + 1, month=1)
            else:
                next_month = month_start.replace(month=month_start.month + 1)
            month_end = next_month - timedelta(days=1)
        
        month_stats = Task.objects.filter(
            created_at__date__gte=month_start,
            created_at__date__lte=month_end
        ).aggregate(
            created_count=Count('id'),
            completed_count=Count('id', filter=Q(
                completed=True,
                updated_at__date__gte=month_start,
                updated_at__date__lte=month_end
            ))
        )
        
        monthly_stats.append({
            'month': month_start.strftime('%Y-%m'),
            'created': month_stats['created_count'] or 0,
            'completed': month_stats['completed_count'] or 0
        })
    
    context = {
        'task_stats': task_stats,
        'tasks_by_user': tasks_by_user,
        'all_tasks': all_tasks,
        'monthly_stats': list(reversed(monthly_stats)),
        'total_task_count': Task.objects.count(),
    }
    
    return render(request, 'admin/analytics/task_analytics.html', context)


# API Views for AJAX requests
@api_view(['GET'])
@permission_classes([IsAdminUser])
def api_dashboard_stats(request):
    """API endpoint for dashboard statistics using PostgreSQL aggregation"""
    
    task_stats = Task.objects.aggregate(
        total_tasks=Count('id'),
        completed_tasks=Count('id', filter=Q(completed=True)),
        pending_tasks=Count('id', filter=Q(completed=False))
    )
    
    user_stats = User.objects.aggregate(
        total_users=Count('id')
    )
    
    completion_rate = 0
    if task_stats['total_tasks'] > 0:
        completion_rate = (task_stats['completed_tasks'] / task_stats['total_tasks']) * 100
    
    return Response({
        'total_tasks': task_stats['total_tasks'],
        'completed_tasks': task_stats['completed_tasks'],
        'pending_tasks': task_stats['pending_tasks'],
        'total_users': user_stats['total_users'],
        'completion_rate': round(completion_rate, 2),
    })


@api_view(['GET'])
@permission_classes([IsAdminUser])
def api_user_stats(request):
    """API endpoint for user statistics using PostgreSQL aggregation"""
    
    users_with_stats = User.objects.annotate(
        task_count=Count('tasks'),
        completed_count=Count('tasks', filter=Q(tasks__completed=True)),
        pending_count=Count('tasks', filter=Q(tasks__completed=False))
    ).order_by('-task_count')
    
    data = []
    for user in users_with_stats:
        completion_rate = (user.completed_count / user.task_count * 100) if user.task_count > 0 else 0
        data.append({
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'task_count': user.task_count,
            'completed_count': user.completed_count,
            'pending_count': user.pending_count,
            'completion_rate': round(completion_rate, 2),
        })
    
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def api_daily_stats(request):
    """API endpoint for daily task statistics using PostgreSQL aggregation"""
    
    days = int(request.GET.get('days', 7))
    
    daily_stats = []
    for i in range(days):
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
    
    return Response(list(reversed(daily_stats)))


@staff_member_required
@cache_page(60 * 15)  # Cache for 15 minutes
def analytics_summary_json(request):
    """JSON endpoint for analytics summary using PostgreSQL aggregation"""
    
    # Overall statistics
    task_overview = Task.objects.aggregate(
        total_tasks=Count('id'),
        completed_tasks=Count('id', filter=Q(completed=True)),
        pending_tasks=Count('id', filter=Q(completed=False))
    )
    
    user_overview = User.objects.aggregate(
        total_users=Count('id')
    )
    
    # Top users by task count
    top_users = list(
        User.objects.annotate(
            task_count=Count('tasks')
        ).filter(task_count__gt=0).order_by('-task_count')[:5].values(
            'email', 'task_count'
        )
    )
    
    # Recent activity
    recent_activity = list(
        Task.objects.select_related('user').order_by('-created_at')[:5].values(
            'title', 'user__email', 'completed', 'created_at'
        )
    )
    
    summary = {
        'overview': {
            **task_overview,
            **user_overview,
        },
        'top_users': top_users,
        'recent_activity': recent_activity
    }
    
    return JsonResponse(summary)
