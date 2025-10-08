from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

from register.admin import register_admin_site
from exam1.admin import exam_admin_site  # 👈 Make sure this exists

urlpatterns = [
    # Default Django admin
    path('admin/', admin.site.urls),

    # Custom admin panels
    path('register-admin/', register_admin_site.urls),  # Custom admin for 'register' app
    path('exam-admin/', exam_admin_site.urls),          # Custom admin for 'exam1' app

    # App URL
    path('registration/', include('register.urls')),
    path('', include('exam1.urls')),
    
    #send massage to email
    
]
