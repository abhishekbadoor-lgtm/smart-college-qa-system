# qa/admin.py

from django.contrib import admin
from .models import Question, Answer, ChatbotKnowledgeBase, ChatMessage


class AnswerInline(admin.TabularInline):
    """Inline admin for answers within question admin."""
    model = Answer
    extra = 0
    fields = ['user', 'answer_text', 'is_verified', 'created_at']
    readonly_fields = ['created_at']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Admin interface for Question model."""
    list_display = ['title', 'user', 'department', 'answer_count', 'is_verified', 'created_at']
    list_filter = ['department', 'is_verified', 'created_at']
    search_fields = ['title', 'description', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [AnswerInline]
    
    fieldsets = (
        ('Question Details', {
            'fields': ('title', 'description', 'user', 'department')
        }),
        ('Moderation', {
            'fields': ('is_verified',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    """Admin interface for Answer model."""
    list_display = ['question', 'user', 'author_role', 'is_verified', 'created_at']
    list_filter = ['is_verified', 'created_at']
    search_fields = ['answer_text', 'user__username', 'question__title']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Answer Details', {
            'fields': ('question', 'user', 'answer_text')
        }),
        ('Moderation', {
            'fields': ('is_verified',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ChatbotKnowledgeBase)
class ChatbotKnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = ['keyword', 'department', 'created_at']
    list_filter = ['department', 'created_at']
    search_fields = ['keyword', 'answer']
    
    fieldsets = (
        ('Knowledge Base Rule', {
            'fields': ('keyword', 'answer', 'department')
        }),
    )


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['user', 'message', 'is_bot', 'timestamp']
    list_filter = ['is_bot', 'timestamp', 'user']
    search_fields = ['message', 'user__username']
    readonly_fields = ['timestamp']
    
    def has_add_permission(self, request):
        return False  # Chat messages are created by system/users only

