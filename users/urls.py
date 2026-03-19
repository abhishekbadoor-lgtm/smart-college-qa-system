# users/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_choice_view, name='register_choice'),
    path('register/student/', views.student_register_view, name='student_register'),
    path('register/faculty/', views.faculty_register_view, name='faculty_register'),
    
    # Student Dashboard
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/attendance/', views.student_attendance, name='student_attendance'),
    path('dashboard/marks/', views.student_marks, name='student_marks'),
    path('dashboard/notices/', views.student_notices, name='student_notices'),
    path('dashboard/qa/', views.student_qa, name='student_qa'),

    # Faculty Dashboard
    path('dashboard/faculty/', views.faculty_dashboard, name='faculty_dashboard'),
    path('dashboard/faculty/students/', views.faculty_student_list, name='faculty_student_list'),
    path('dashboard/faculty/attendance/add/', views.faculty_add_attendance, name='faculty_add_attendance'),
    path('dashboard/faculty/marks/add/', views.faculty_add_marks, name='faculty_add_marks'),
    path('dashboard/faculty/notices/add/', views.faculty_add_notice, name='faculty_add_notice'),
]