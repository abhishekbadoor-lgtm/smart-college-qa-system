from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='admin_dashboard'),
    
    # Faculty Management
    path('faculty/', views.faculty_list, name='admin_faculty_list'),
    path('faculty/verify/<int:pk>/', views.verify_faculty, name='admin_verify_faculty'),
    path('faculty/delete/<int:pk>/', views.delete_faculty, name='admin_delete_faculty'),
    path('faculty/view/<int:pk>/', views.faculty_detail, name='admin_faculty_detail'),
    
    # Student Management
    path('students/', views.student_list, name='admin_student_list'),
    path('students/verify/<int:pk>/', views.verify_student, name='admin_verify_student'),
    path('students/delete/<int:pk>/', views.delete_student, name='admin_delete_student'),
    path('students/view/<int:pk>/', views.student_detail, name='admin_student_detail'),
    path('students/edit/<int:pk>/', views.edit_student, name='admin_edit_student'),
    path('students/add/', views.add_student, name='admin_add_student'),
    
    # Course Management
    path('courses/', views.course_list, name='admin_course_list'),
    path('courses/add/', views.add_course, name='admin_add_course'),
    path('courses/view/<int:pk>/', views.course_detail, name='admin_course_detail'),
    path('courses/edit/<int:pk>/', views.edit_course, name='admin_edit_course'),
    path('courses/delete/<int:pk>/', views.delete_course, name='admin_delete_course'),
    
    # Notice Management
    path('notices/', views.notice_list, name='admin_notice_list'),
    path('notices/add/', views.add_notice, name='admin_add_notice'),
    path('notices/delete/<int:pk>/', views.delete_notice, name='admin_delete_notice'),
    
    # Feedback Management
    path('feedback/', views.feedback_list, name='admin_feedback_list'),
    path('feedback/view/<int:pk>/', views.feedback_detail, name='admin_feedback_detail'),
    
    # Q&A Management
    path('qa/', views.qa_list, name='admin_qa_list'),
    path('qa/question/delete/<int:pk>/', views.qa_delete_question, name='admin_qa_delete_question'),
    path('qa/answer/delete/<int:pk>/', views.qa_delete_answer, name='admin_qa_delete_answer'),
    path('qa/question/verify/<int:pk>/', views.qa_verify_question, name='admin_qa_verify_question'),
    
    # Chatbot Knowledge Base
    path('chatbot/', views.chatbot_list, name='admin_chatbot_list'),
    path('chatbot/add/', views.add_chatbot_rule, name='admin_add_chatbot_rule'),
    path('chatbot/edit/<int:pk>/', views.edit_chatbot_rule, name='admin_edit_chatbot_rule'),
    path('chatbot/delete/<int:pk>/', views.delete_chatbot_rule, name='admin_delete_chatbot_rule'),
    path('chatbot/bulk-upload/', views.bulk_upload_chatbot_rules, name='admin_bulk_upload_chatbot_rules'),
]
