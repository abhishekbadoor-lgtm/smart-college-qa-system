from django.urls import path
from . import views

urlpatterns = [
    path('mark-attendance/', views.mark_attendance, name='mark_attendance'),
    path('add-marks/', views.add_marks, name='add_marks'),
    
    # Feedback URLs
    path('feedback/create/', views.student_feedback_create, name='student_feedback_create'),
    path('feedback/my-feedbacks/', views.student_feedback_list, name='student_feedback_list'),
    path('feedback/faculty/list/', views.faculty_feedback_list, name='faculty_feedback_list'),
    path('feedback/faculty/reply/<int:pk>/', views.faculty_feedback_reply, name='faculty_feedback_reply'),
]
