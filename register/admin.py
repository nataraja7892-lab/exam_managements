# register/admin.py
from django.contrib import admin
from django.contrib.admin import AdminSite
from .models import Student

class RegisterAdminSite(AdminSite):
    site_header = 'Register Admin'

# Register the custom admin site
register_admin_site = RegisterAdminSite(name='register_admin')

# Register the models
register_admin_site.register(Student)
