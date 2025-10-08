from django.urls import path
from . import views
from register.views import register_student, success_view

app_name = 'exam1'

urlpatterns = [
    path('create/', views.create_exam, name='create_exam'),
    path('list/', views.exam_list, name='exam_list'),
    path('update/<int:exam_id>/', views.update_exam, name='update_exam'),
    path('delete/<int:exam_id>/', views.delete_exam, name='delete_exam'),

    # Results
    path('enter_results/', views.enter_results, name='enter_results'),
    path('view_results/', views.view_results, name='view_results'),
    path('download_result/<int:student_id>/<int:exam_id>/', views.download_student_result_pdf, name='download_student_result'),
    path("delete-result/<int:student_id>/<int:exam_id>/", views.delete_result, name="delete_result"),

    # Dashboard & Students
    path('', views.dashboard, name='dashboard'),
    path('students/', views.total_students, name='students_by_course'),
    path('students/passed/', views.passed_students_by_course, name='passed_students_by_course'),
    path("students/failed/all/", views.all, name="all_failed_students"),

    # Exams
    path("exams/total/", views.total_exams_view, name="total_exams"),

    # Passed students flow
    path("students/passed/courses/", views.passed_courses, name="passed"),
    path("students/passed/<str:course_name>/", views.passed_exams_by_course, name="passed_exams"),
    path("students/passed/<str:course_name>/<str:exam_id>/", views.passed_students_by_course_exam, name="passed_students_list"),

    # Register
    path('register/', register_student, name='register_student'),

    # ✅ Send PDF to email
    path("send-result/<int:student_id>/<int:exam_id>/", views.send_result_email, name="send_result"),
    path('send-all-results/<int:exam_id>/', views.send_all_results_email, name='send_all_results_email'),
    #this is details
    path("details/", views.manage_students, name="manage_students"),
    #ranking
    path("ranking/", views.ranking, name="ranking"),
    
    #admin
   
]
