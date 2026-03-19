# users/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import StudentProfile, FacultyProfile
from cms.models import Course # Import Course to use in a ChoiceField

# ------------------------------------
# 1. Student Registration Form
# ------------------------------------
class StudentRegistrationForm(UserCreationForm):
    # Additional fields for the StudentProfile model
    roll_number = forms.CharField(max_length=15, help_text='Enter your unique Roll Number')
    
    # Use the Course model for a selection field
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        empty_label="Select your Course",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta(UserCreationForm.Meta):
        # We inherit from UserCreationForm for username, email, password
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name')

    def clean_roll_number(self):
        roll_number = self.cleaned_data.get('roll_number')
        if StudentProfile.objects.filter(roll_number=roll_number).exists():
            raise forms.ValidationError("A student with this Roll Number already exists.")
        return roll_number


# ------------------------------------
# 2. Faculty Registration Form
# ------------------------------------
class FacultyRegistrationForm(UserCreationForm):
    # Additional fields for the FacultyProfile model
    employee_id = forms.CharField(max_length=15, help_text='Enter your Employee ID')
    department = forms.CharField(max_length=100, help_text='Enter your Department (e.g., Computer Science)')
    
    class Meta(UserCreationForm.Meta):
        # We inherit from UserCreationForm for username, email, password
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name')

    def clean_employee_id(self):
        employee_id = self.cleaned_data.get('employee_id')
        if FacultyProfile.objects.filter(employee_id=employee_id).exists():
            raise forms.ValidationError("A faculty with this Employee ID already exists.")
        return employee_id