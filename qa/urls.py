# qa/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Chat interface (Main QA View)
    path('', views.chat_view, name='qa_list'),  # Replaces the old list view
    
    # API for chatbot
    path('get-response/', views.get_bot_response, name='qa_get_response'),
    path('clear-chat/', views.clear_chat, name='qa_clear_chat'),
    
    # Keep old views accessible if needed, or redirect them
    path('ask/', views.ask_question, name='qa_ask'),
    path('question/<int:pk>/', views.question_detail, name='qa_detail'),
    path('question/<int:pk>/answer/', views.submit_answer, name='qa_answer'),
    path('answer/<int:pk>/verify/', views.verify_answer, name='qa_verify_answer'),
]
