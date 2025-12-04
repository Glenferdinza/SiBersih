from django.contrib import admin
from django.contrib.admin import AdminSite
from django.shortcuts import redirect

class CustomAdminSite(AdminSite):
    site_header = 'SiBersih Administration'
    site_title = 'SiBersih Admin'
    index_title = 'Dashboard'
    
    def login(self, request, extra_context=None):
        """Override login to redirect authenticated admins to custom dashboard"""
        if request.user.is_authenticated and request.user.role == 'admin':
            return redirect('core:admin_dashboard')
        return super().login(request, extra_context)
    
    def index(self, request, extra_context=None):
        """Override index to redirect to custom dashboard"""
        if request.user.is_authenticated and request.user.role == 'admin':
            return redirect('core:admin_dashboard')
        return super().index(request, extra_context)

# Create custom admin site instance
custom_admin_site = CustomAdminSite(name='custom_admin')

# Register your models here.
