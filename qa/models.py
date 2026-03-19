# qa/models.py

from django.db import models
from django.contrib.auth.models import User
from users.models import StudentProfile, FacultyProfile


class Question(models.Model):
    """
    Represents a question posted by a student in the Q&A discussion forum.
    """
    title = models.CharField(max_length=255, help_text="Short title of the question")
    description = models.TextField(help_text="Detailed description of the question")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions')
    
    # Department choices for filtering
    DEPARTMENT_CHOICES = [
        ('CS', 'Computer Science'),
        ('IT', 'Information Technology'),
        ('EC', 'Electronics & Communication'),
        ('EE', 'Electrical Engineering'),
        ('ME', 'Mechanical Engineering'),
        ('CE', 'Civil Engineering'),
        ('GEN', 'General'),
        ('OTH', 'Other'),
    ]
    department = models.CharField(
        max_length=3, 
        choices=DEPARTMENT_CHOICES, 
        default='GEN',
        help_text="Department/category for this question"
    )
    
    # Admin moderation
    is_verified = models.BooleanField(
        default=False, 
        help_text="Admin can mark important/verified questions"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']  # Latest questions first
        
    def __str__(self):
        return self.title
    
    def answer_count(self):
        """Returns the number of answers for this question."""
        return self.answers.count()
    
    def has_verified_answer(self):
        """Checks if this question has at least one verified answer."""
        return self.answers.filter(is_verified=True).exists()
    
    def author_role(self):
        """Returns the role of the question author."""
        if self.user.is_superuser:
            return "Admin"
        elif hasattr(self.user, 'facultyprofile'):
            return "Faculty"
        elif hasattr(self.user, 'studentprofile'):
            return "Student"
        return "User"


class Answer(models.Model):
    """
    Represents an answer to a question in the Q&A discussion forum.
    Can be posted by students, faculty, or admin.
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    answer_text = models.TextField(help_text="The answer content")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answers')
    
    # Verification - faculty or admin can mark answers as verified/authoritative
    is_verified = models.BooleanField(
        default=False,
        help_text="Verified answers are marked as authoritative"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']  # Oldest answers first (chronological)
        
    def __str__(self):
        return f"Answer by {self.user.username} on {self.question.title[:30]}"
    
    def author_role(self):
        """Returns the role of the answer author."""
        if self.user.is_superuser:
            return "Admin"
        elif hasattr(self.user, 'facultyprofile'):
            return "Faculty"
        elif hasattr(self.user, 'studentprofile'):
            return "Student"
        return "User"


class ChatbotKnowledgeBase(models.Model):
    """
    Stores keywords and automated responses for the chatbot.
    Managed by Admin.
    """
    keyword = models.CharField(max_length=255, help_text="Keyword or trigger question (e.g., 'exam date', 'hostel fee')")
    answer = models.TextField(help_text="The automated answer to be shown")
    
    # Department choices (reusing from Question model)
    department = models.CharField(
        max_length=3, 
        choices=Question.DEPARTMENT_CHOICES, 
        default='GEN',
        help_text="Department context for this rule"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Rule: {self.keyword}"


class ChatMessage(models.Model):
    """
    Stores the chat history between users and the bot.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_messages', null=True, blank=True)
    message = models.TextField()
    is_bot = models.BooleanField(default=False, help_text="True if message is from the system/bot")
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['timestamp']
        
    def __str__(self):
        sender = "Bot" if self.is_bot else self.user.username
        return f"{sender}: {self.message[:50]}"

