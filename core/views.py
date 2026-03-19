from django.shortcuts import render, redirect
from cms.models import Notice
from users.models import StudentProfile, FacultyProfile
from django.contrib.auth import logout
from django.db.models import Q


def home(request):
    if request.user.is_authenticated:
        return login_redirect(request)
    # Show latest public notices on the homepage
    notices = Notice.objects.filter(is_public=True).order_by('-date_posted')[:10]
    return render(request, 'core/index.html', {'notices': notices})


def login_redirect(request):
	"""Redirect users to appropriate dashboard based on their role"""
	if not request.user.is_authenticated:
		return redirect('login')
	
	# Check if superuser (admin)
	if request.user.is_superuser:
		return redirect('admin_dashboard')
	
	# Check if student
	try:
		student = StudentProfile.objects.get(user=request.user)
		return redirect('student_dashboard')
	except StudentProfile.DoesNotExist:
		pass
	
	# Check if faculty
	try:
		faculty = FacultyProfile.objects.get(user=request.user)
		return redirect('faculty_dashboard')
	except FacultyProfile.DoesNotExist:
		pass
	
	# Default fallback
	return redirect('home')


def custom_logout(request):
	"""Custom logout view that redirects to home immediately"""
	logout(request)
	return redirect('home')


def public_qa(request):
	"""Redirect to the new Q&A discussion forum"""
	return redirect('qa_list')
