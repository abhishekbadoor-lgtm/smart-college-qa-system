# users/models.py

from django.db import models
from django.contrib.auth.models import User

# ------------------------------------
# 1. Student Profile
# ------------------------------------
class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    roll_number = models.CharField(max_length=15, unique=True)
    course = models.ForeignKey('cms.Course', on_delete=models.SET_NULL, null=True, blank=True)
    current_semester = models.PositiveIntegerField(default=1)
    
    # We will just store a simple text string for the timetable for now
    timetable_details = models.TextField(blank=True) 
    
    # Admin Verification
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"Student: {self.user.username} ({self.roll_number})"

# ------------------------------------
# 2. Faculty Profile
# ------------------------------------
class FacultyProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    employee_id = models.CharField(max_length=15, unique=True)
    department = models.CharField(max_length=100)
    
    # CRITICAL FIELD for Admin Verification
    is_verified = models.BooleanField(default=False) 

    def __str__(self):
        return f"Faculty: {self.user.username} (Verified: {self.is_verified})"