from django.contrib import admin
from .models import StudentProfile, FacultyProfile


@admin.action(description='Verify selected faculty accounts')
def verify_faculty(modeladmin, request, queryset):
	updated = queryset.update(is_verified=True)
	modeladmin.message_user(request, f"{updated} faculty account(s) marked as verified.")


@admin.register(FacultyProfile)
class FacultyProfileAdmin(admin.ModelAdmin):
	list_display = ('user', 'employee_id', 'department', 'is_verified')
	list_filter = ('is_verified', 'department')
	actions = [verify_faculty]


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
	list_display = ('user', 'roll_number', 'course')
	search_fields = ('user__username', 'roll_number')
