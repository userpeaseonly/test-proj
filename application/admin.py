from django.contrib import admin
from django.contrib.admin import AdminSite
from django.urls import reverse
from django.http import HttpResponseRedirect


class RestrictedAdminSite(AdminSite):
    """
    Custom admin site that is minimal and clean.
    Only shows essential admin functionality.
    """
    site_header = 'Administration Panel'
    site_title = 'Admin'
    index_title = 'Site Administration'
    
    def index(self, request, extra_context=None):
        """
        Custom admin index with minimal clean interface
        """
        from django.shortcuts import render
        
        context = {
            'title': 'Site Administration',
            'app_list': [],  # Empty app list for clean interface
            'has_permission': self.has_permission(request),
        }
        
        if extra_context:
            context.update(extra_context)
            
        return render(request, 'admin/index_clean.html', context)
    
    def has_permission(self, request):
        """
        Only allow superusers or admin role users
        """
        return (
            request.user.is_active and 
            (request.user.is_superuser or 
             (hasattr(request.user, 'role') and request.user.role == 'admin'))
        )


# Create the restricted admin site
restricted_admin_site = RestrictedAdminSite(name='restricted_admin')

# Remove Groups from default admin site
try:
    from django.contrib.auth.models import Group
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass  # Already unregistered

# Override the default admin site
admin.site = restricted_admin_site
admin.sites.site = restricted_admin_site