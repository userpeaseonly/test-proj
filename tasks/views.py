from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Q
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from application.throttles import (
    TaskCreateRateThrottle, TaskUpdateRateThrottle, BurstRateThrottle,
    LowSecurityThrottle, MediumSecurityThrottle
)
from .models import Task
from .serializers import (
    TaskSerializer, 
    TaskCreateUpdateSerializer, 
    TaskListSerializer,
    TaskStatsSerializer
)


class TaskListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [TaskCreateRateThrottle, BurstRateThrottle]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['completed']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'title']
    ordering = ['-created_at']

    def get_queryset(self):
        # Users can only see their own tasks
        return Task.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TaskCreateUpdateSerializer
        return TaskListSerializer

    @extend_schema(
        summary="List user's tasks",
        description="Get a list of all tasks belonging to the authenticated user. Supports filtering, searching, and ordering.",
        parameters=[
            OpenApiParameter(name='completed', type=OpenApiTypes.BOOL, description='Filter by completion status'),
            OpenApiParameter(name='search', type=OpenApiTypes.STR, description='Search in title and description'),
            OpenApiParameter(name='ordering', type=OpenApiTypes.STR, description='Order by: created_at, updated_at, title (prefix with - for descending)')
        ],
        responses={200: TaskListSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Create a new task",
        description="Create a new task for the authenticated user",
        request=TaskCreateUpdateSerializer,
        responses={201: TaskSerializer}
    )
    def post(self, request, *args, **kwargs):
        serializer = TaskCreateUpdateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        task = serializer.save(user=request.user)
        return Response(TaskSerializer(task).data, status=status.HTTP_201_CREATED)


class TaskRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [TaskUpdateRateThrottle, BurstRateThrottle]

    def get_queryset(self):
        # Users can only access their own tasks
        return Task.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return TaskCreateUpdateSerializer
        return TaskSerializer

    @extend_schema(
        summary="Get task details",
        description="Retrieve detailed information about a specific task",
        responses={200: TaskSerializer}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Update task",
        description="Update a specific task (full update)",
        request=TaskCreateUpdateSerializer,
        responses={200: TaskSerializer}
    )
    def put(self, request, *args, **kwargs):
        task = self.get_object()
        serializer = TaskCreateUpdateSerializer(task, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        updated_task = serializer.save()
        return Response(TaskSerializer(updated_task).data)

    @extend_schema(
        summary="Partially update task",
        description="Partially update a specific task",
        request=TaskCreateUpdateSerializer,
        responses={200: TaskSerializer}
    )
    def patch(self, request, *args, **kwargs):
        task = self.get_object()
        serializer = TaskCreateUpdateSerializer(task, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        updated_task = serializer.save()
        return Response(TaskSerializer(updated_task).data)

    @extend_schema(
        summary="Delete task",
        description="Delete a specific task permanently",
        responses={204: None}
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


@extend_schema(
    summary="Mark task as completed",
    description="Mark a specific task as completed",
    request=None,
    responses={200: TaskSerializer}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([TaskUpdateRateThrottle, BurstRateThrottle])
def mark_task_completed(request, pk):
    """Mark a task as completed"""
    try:
        task = Task.objects.get(pk=pk, user=request.user)
        task.completed = True
        task.save()
        return Response(TaskSerializer(task).data)
    except Task.DoesNotExist:
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)


@extend_schema(
    summary="Mark task as pending",
    description="Mark a specific task as pending (not completed)",
    request=None,
    responses={200: TaskSerializer}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([TaskUpdateRateThrottle, BurstRateThrottle])
def mark_task_pending(request, pk):
    """Mark a task as pending"""
    try:
        task = Task.objects.get(pk=pk, user=request.user)
        task.completed = False
        task.save()
        return Response(TaskSerializer(task).data)
    except Task.DoesNotExist:
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)


@extend_schema(
    summary="Toggle task completion",
    description="Toggle the completion status of a specific task",
    request=None,
    responses={200: TaskSerializer}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([TaskUpdateRateThrottle, BurstRateThrottle])
def toggle_task_completion(request, pk):
    """Toggle task completion status"""
    try:
        task = Task.objects.get(pk=pk, user=request.user)
        task.completed = not task.completed
        task.save()
        return Response(TaskSerializer(task).data)
    except Task.DoesNotExist:
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)


@extend_schema(
    summary="Get task statistics",
    description="Get statistics about the user's tasks (total, completed, pending, completion rate)",
    responses={200: TaskStatsSerializer}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@throttle_classes([LowSecurityThrottle])
def task_stats(request):
    """Get user's task statistics"""
    user_tasks = Task.objects.filter(user=request.user)
    
    total_tasks = user_tasks.count()
    completed_tasks = user_tasks.filter(completed=True).count()
    pending_tasks = total_tasks - completed_tasks
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    stats = {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'completion_rate': round(completion_rate, 2)
    }
    
    return Response(stats)

