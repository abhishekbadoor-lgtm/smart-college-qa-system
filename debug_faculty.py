
import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_project.settings')
django.setup()

from users.models import FacultyProfile
from cms.models import Course
from django.db.models import Q
from django.contrib.auth.models import User

print("Starting debug...")

try:
    # 1. Check Course import
    print(f"Course model: {Course}")

    # 2. Simulate GET logic
    # Find a faculty
    faculty = FacultyProfile.objects.first()
    if not faculty:
        print("No faculty found, creating one for test.")
        # Create dummy faculty if needed, or just skip
        sys.exit("No faculty to test with.")
    
    print(f"Testing with faculty: {faculty}")
    dept = faculty.department
    print(f"Department: {dept}")
    
    courses = Course.objects.none()
    if dept:
        courses = Course.objects.filter(Q(code__istartswith=dept) | Q(name__icontains=dept))
    
    print(f"Courses query: {courses}")
    print(f"Courses count: {courses.count()}")

    print("Logic executed successfully.")

except Exception as e:
    print(f"CRASHED: {e}")
    import traceback
    traceback.print_exc()
