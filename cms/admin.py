from django.contrib import admin
from .models import Course, Semester, Subject, Notice, InternalMark, Feedback


@admin.action(description='Verify selected marks')
def verify_marks(modeladmin, request, queryset):
	updated = queryset.update(is_verified=True)
	modeladmin.message_user(request, f"{updated} mark(s) marked as verified.")


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
	list_display = ('code', 'name')


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
	list_display = ('course', 'semester_number')
	list_filter = ('course',)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
	list_display = ('code', 'name', 'semester', 'faculty')
	list_filter = ('semester__course', 'faculty')


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
	list_display = ('title', 'date_posted', 'is_public', 'faculty_posted')
	list_filter = ('is_public', 'date_posted')


@admin.register(InternalMark)
class InternalMarkAdmin(admin.ModelAdmin):
	list_display = ('student', 'subject', 'mark_type', 'score', 'is_verified', 'date_entered')
	list_filter = ('is_verified', 'mark_type', 'subject__semester__course')
	actions = [verify_marks]


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
	list_display = ('name', 'email', 'date_submitted')
	readonly_fields = ('date_submitted',)
