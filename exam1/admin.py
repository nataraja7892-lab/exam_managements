# exam1/admin.py
from django.contrib.admin import AdminSite
from .models import Exam
from .models import Result
from django.contrib import admin

class ExamAdminSite(AdminSite):
    site_header = 'Exam Admin'

exam_admin_site = ExamAdminSite(name='exam_admin')

# Register your models
exam_admin_site.register(Exam)
exam_admin_site.register(Result)
