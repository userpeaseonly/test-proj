from django.contrib import admin
from .models import Task


# @admin.register(Task)
# class TaskAdmin(admin.ModelAdmin):
#     list_display = ('title', 'user', 'completed', 'created_at', 'updated_at')
#     list_filter = ('completed', 'created_at', 'updated_at', 'user')
#     search_fields = ('title', 'description', 'user__email', 'user__first_name', 'user__last_name')
#     readonly_fields = ('created_at', 'updated_at')
#     date_hierarchy = 'created_at'
    
#     fieldsets = (
#         (None, {
#             'fields': ('title', 'description', 'user')
#         }),
#         ('Status', {
#             'fields': ('completed',)
#         }),
#         ('Timestamps', {
#             'fields': ('created_at', 'updated_at'),
#             'classes': ('collapse',)
#         }),
#     )
    
#     def get_queryset(self, request):
#         qs = super().get_queryset(request)
#         if request.user.is_superuser:
#             return qs
#         # If user is admin but not superuser, they can see all tasks
#         if hasattr(request.user, 'role') and request.user.role == 'admin':
#             return qs
#         # Regular users can only see their own tasks
#         return qs.filter(user=request.user)
    
#     def has_change_permission(self, request, obj=None):
#         # Admin can change any task, regular users only their own
#         if obj is None:
#             return True
#         if request.user.is_superuser or (hasattr(request.user, 'role') and request.user.role == 'admin'):
#             return True
#         return obj.user == request.user
    
#     def has_delete_permission(self, request, obj=None):
#         # Admin can delete any task, regular users only their own
#         if obj is None:
#             return True
#         if request.user.is_superuser or (hasattr(request.user, 'role') and request.user.role == 'admin'):
#             return True
#         return obj.user == request.user
