# cms/models.py

from django.db import models
from users.models import FacultyProfile, StudentProfile

# ------------------------------------
# 1. Course Information (for linking)
# ------------------------------------
class Course(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def total_subjects(self):
        return Subject.objects.filter(semester__course=self).count()

class Semester(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='semesters')
    semester_number = models.PositiveIntegerField()

    class Meta:
        unique_together = ('course', 'semester_number')
        ordering = ['semester_number']

    def __str__(self):
        return f"{self.course.code} - Semester {self.semester_number}"

class Subject(models.Model):
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='subjects')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    faculty = models.ForeignKey(FacultyProfile, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.code} - {self.name} (Sem {self.semester.semester_number})"

# ------------------------------------
# 2. Notice Board Module
# ------------------------------------
class Notice(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)
    
    # Determines visibility
    is_public = models.BooleanField(default=True) # True for General College Notice
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True, blank=True)
    faculty_posted = models.ForeignKey(FacultyProfile, on_delete=models.SET_NULL, null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text="Notice will disappear after this time")
    
    class Meta:
        ordering = ['-date_posted'] # Latest notice first

    def __str__(self):
        return self.title



# ------------------------------------
# 4. Internal Marks Module
# ------------------------------------
class InternalMark(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    faculty = models.ForeignKey(FacultyProfile, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True, blank=True)
    
    MARK_CHOICES = [
        ('A1', 'Assignment 1'),
        ('QZ', 'Quiz'),
        ('M1', 'Midterm 1'),
        ('PR', 'Practical'),
        ('OT', 'Other'),
    ]
    
    mark_type = models.CharField(max_length=2, choices=MARK_CHOICES)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    date_entered = models.DateTimeField(auto_now_add=True)
    # Marks are visible to students immediately
    is_verified = models.BooleanField(default=True)

    class Meta:
        # Prevents a faculty from entering the same mark type twice for the same student/subject
        unique_together = ('student', 'subject', 'mark_type') 
        
    def __str__(self):
        return f"{self.student.user.username} - {self.subject.code} ({self.mark_type})"

# ------------------------------------
# 5. Feedback Module
# ------------------------------------
class Feedback(models.Model):
    RECIPIENT_CHOICES = [
        ('ADMIN', 'Admin'),
        ('FACULTY', 'Faculty'),
    ]
    
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100) # For non-logged-in users
    email = models.EmailField()
    recipient_type = models.CharField(max_length=10, choices=RECIPIENT_CHOICES, default='ADMIN')
    faculty = models.ForeignKey(FacultyProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_feedbacks')
    message = models.TextField()
    date_submitted = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        dest = f"to {self.recipient_type}"
        if self.recipient_type == 'FACULTY' and self.faculty:
            dest = f"to Faculty: {self.faculty.user.username}"
        return f"Feedback from {self.name} {dest} on {self.date_submitted.date()}"
        
    # Reply (can be from Admin or Faculty)
    reply = models.TextField(blank=True, null=True, help_text="Reply to this feedback")
    replied_at = models.DateTimeField(blank=True, null=True)

# ------------------------------------
# 6. Attendance Module
# ------------------------------------
class Attendance(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField()
    
    STATUS_CHOICES = [
        ('P', 'Present'),
        ('A', 'Absent'),
    ]
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')
    
    class Meta:
        unique_together = ('student', 'subject', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.student.user.username} - {self.subject.code} - {self.date} ({self.status})"