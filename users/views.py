# users/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.decorators import login_required
from .forms import StudentRegistrationForm, FacultyRegistrationForm
from .models import FacultyProfile, StudentProfile
from cms.models import Attendance, InternalMark, Notice, Course, Semester, Subject
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.utils import timezone
import datetime

# ------------------------------------
# 1. Registration Choice View
# ------------------------------------
def register_choice_view(request):
    """Page for user to select if they are a Student or Faculty."""
    return render(request, 'users/register_choice.html')


# ------------------------------------
# 2. Student Registration View
# ------------------------------------
def student_register_view(request):
    """
    Public student registration is now DISABLED.
    Students must be registered by an administrator.
    """
    messages.warning(request, "Student registration is currently restricted to administrators only. If you need an account, please contact your administration office.")
    return redirect('login')


# ------------------------------------
# 3. Faculty Registration View (with is_verified=False)
# ------------------------------------
def faculty_register_view(request):
    if request.method == 'POST':
        form = FacultyRegistrationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                # 1. Save the basic User object
                user = form.save()
                user.first_name = form.cleaned_data.get('first_name')
                user.last_name = form.cleaned_data.get('last_name')
                user.email = form.cleaned_data.get('email')
                user.save() 

                # 2. Save the FacultyProfile object with is_verified=False
                FacultyProfile.objects.create(
                    user=user,
                    employee_id=form.cleaned_data.get('employee_id'),
                    department=form.cleaned_data.get('department'),
                    is_verified=False
                )

            
            messages.info(request, 'Faculty registration submitted! Your account requires **Admin verification** before you can access all features.')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = FacultyRegistrationForm()
        
    context = {'form': form}
    return render(request, 'users/faculty_register.html', context)

# ------------------------------------
# 4. Student Dashboard
# ------------------------------------
@login_required
def student_dashboard(request):
    try:
        student = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        messages.error(request, 'You are not registered as a student.')
        return redirect('home')
    
    # Check if verified
    if not student.is_verified:
        messages.warning(request, 'Your account is pending admin verification.')
    
    # Get attendance summary
    total_classes = Attendance.objects.filter(student=student).count()
    present_count = Attendance.objects.filter(student=student, status='P').count()
    attendance_percentage = (present_count / total_classes * 100) if total_classes > 0 else 0
    
    # Get recent marks (only those with assigned subjects)
    recent_marks = InternalMark.objects.filter(student=student, subject__isnull=False).order_by('-date_entered')[:5]
    
    # Get recent notices (Public, for their course, or for their current subjects) - Filter out expired ones
    recent_notices = Notice.objects.filter(
        Q(is_public=True) | 
        Q(course=student.course) |
        Q(subject__semester__course=student.course, subject__semester__semester_number=student.current_semester)
    ).filter(
        Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
    ).distinct().order_by('-date_posted')[:5]
    
    context = {
        'student': student,
        'total_classes': total_classes,
        'present_count': present_count,
        'attendance_percentage': round(attendance_percentage, 1),
        'recent_marks': recent_marks,
        'recent_notices': recent_notices,
    }
    return render(request, 'student_dashboard/dashboard.html', context)

@login_required
def student_attendance(request):
    try:
        student = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        messages.error(request, 'You are not registered as a student.')
        return redirect('home')
    
    attendance_records = Attendance.objects.filter(student=student).select_related('subject__semester').order_by('-date')
    
    # Optional: Group by semester for the view if needed. 
    # For now, we'll keep it as a list but ensure subject info is available.
    
    context = {
        'student': student,
        'attendance_records': attendance_records,
    }
    return render(request, 'student_dashboard/attendance.html', context)

@login_required
def student_marks(request):
    try:
        student = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        messages.error(request, 'You are not registered as a student.')
        return redirect('home')
    
    marks = InternalMark.objects.filter(student=student).select_related('subject__semester').order_by('subject__semester__semester_number', 'subject__code')
    
    # Organize marks by semester for the template
    marks_by_semester = {}
    for m in marks:
        # Skip marks with no subject assigned
        if m.subject is None:
            continue
        sem_num = m.subject.semester.semester_number
        if sem_num not in marks_by_semester:
            marks_by_semester[sem_num] = []
        marks_by_semester[sem_num].append(m)
    
    # Sort semesters
    sorted_semesters = sorted(marks_by_semester.keys())
    marks_list = [(s, marks_by_semester[s]) for s in sorted_semesters]
    
    context = {
        'student': student,
        'marks_list': marks_list,
    }
    return render(request, 'student_dashboard/marks.html', context)

@login_required
def student_notices(request):
    try:
        student = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        messages.error(request, 'You are not registered as a student.')
        return redirect('home')
    
    notices = Notice.objects.filter(
        Q(is_public=True) | 
        Q(course=student.course) |
        Q(subject__semester__course=student.course, subject__semester__semester_number=student.current_semester)
    ).filter(
        Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
    ).distinct().order_by('-date_posted')
    
    context = {
        'student': student,
        'notices': notices,
    }
    return render(request, 'student_dashboard/notices.html', context)

@login_required
def student_qa(request):
    """Redirect to the new QA discussion forum."""
    return redirect('qa_list')


# ------------------------------------
# 5. Faculty Dashboard
# ------------------------------------
@login_required
def faculty_dashboard(request):
    try:
        faculty = FacultyProfile.objects.get(user=request.user)
    except FacultyProfile.DoesNotExist:
        messages.error(request, 'You are not registered as a faculty.')
        return redirect('home')
    
    # Simple dashboard stats - Filter out expired ones
    my_notices = Notice.objects.filter(
        faculty_posted=faculty
    ).filter(
        Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
    ).order_by('-date_posted')[:5]
    
    # We can assume faculty is teaching courses related to their department, 
    # but since Course model doesn't link to Faculty directly (only Attendance/Marks do),
    # we might just show notices and actions for now.
    
    context = {
        'faculty': faculty,
        'recent_notices': my_notices,
    }
    return render(request, 'faculty_dashboard/dashboard.html', context)

@login_required
def faculty_student_list(request):
    try:
        faculty = FacultyProfile.objects.get(user=request.user)
    except FacultyProfile.DoesNotExist:
        return redirect('home')

    assigned_subjects = Subject.objects.filter(faculty=faculty).select_related('semester__course')
    
    # Get all unique courses where faculty teaches
    courses = Course.objects.filter(semesters__subjects__faculty=faculty).distinct()
    
    selected_course_id = request.GET.get('course')
    selected_semester_id = request.GET.get('semester')
    selected_subject_id = request.GET.get('subject')
    
    semesters_in_course = []
    subjects_in_semester = []
    students = StudentProfile.objects.none()
    
    if selected_course_id:
        semesters_in_course = Semester.objects.filter(course_id=selected_course_id, subjects__faculty=faculty).distinct()
        
        if selected_semester_id:
            subjects_in_semester = assigned_subjects.filter(semester_id=selected_semester_id)
            
            if selected_subject_id:
                subject = get_object_or_404(assigned_subjects, id=selected_subject_id)
                students = StudentProfile.objects.filter(
                    course=subject.semester.course,
                    current_semester=subject.semester.semester_number,
                    is_verified=True
                ).select_related('user', 'course').order_by('roll_number')
            else:
                sem = get_object_or_404(Semester, id=selected_semester_id)
                students = StudentProfile.objects.filter(
                    course=sem.course,
                    current_semester=sem.semester_number,
                    is_verified=True
                ).select_related('user', 'course').order_by('roll_number')
        else:
            # If only course selected, show all students in that course
            students = StudentProfile.objects.filter(course_id=selected_course_id, is_verified=True).select_related('user', 'course').order_by('roll_number')
    else:
        # Default: Filter by faculty department if nothing selected
        dept = faculty.department
        if dept:
            dept_courses = Course.objects.filter(Q(code__istartswith=dept) | Q(name__icontains=dept))
            students = StudentProfile.objects.filter(course__in=dept_courses).select_related('user', 'course')

    context = {
        'students': students,
        'faculty': faculty,
        'courses': courses,
        'semesters': semesters_in_course,
        'subjects': subjects_in_semester,
        'selected_course_id': int(selected_course_id) if selected_course_id and selected_course_id.isdigit() else None,
        'selected_semester_id': int(selected_semester_id) if selected_semester_id and selected_semester_id.isdigit() else None,
        'selected_subject_id': int(selected_subject_id) if selected_subject_id and selected_subject_id.isdigit() else None,
    }
    return render(request, 'faculty_dashboard/student_list.html', context)

@login_required
def faculty_add_attendance(request):
    try:
        faculty = FacultyProfile.objects.get(user=request.user)
    except FacultyProfile.DoesNotExist:
        return redirect('home')

    # Show only subjects assigned to this faculty
    assigned_subjects = Subject.objects.filter(faculty=faculty).select_related('semester__course')

    if request.method == 'POST':
        selected_course_id = request.POST.get('course')
        selected_semester_id = request.POST.get('semester')
        selected_subject_id = request.POST.get('subject')
        date_str = request.POST.get('date')
        
        # Prevent marking attendance for future dates
        if date_str:
            selected_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            if selected_date > timezone.now().date():
                messages.error(request, "You cannot mark attendance for future dates.")
                return redirect(f"{request.path}?course={selected_course_id}&semester={selected_semester_id}&subject={selected_subject_id}")
        
        # Validate subject against assigned subjects
        subject = get_object_or_404(assigned_subjects, id=selected_subject_id)
        
        count = 0
        for key, value in request.POST.items():
            if key.startswith('status_'):
                student_id = key.split('_')[1]
                try:
                    student = StudentProfile.objects.get(user__id=student_id)
                    # Security check: Ensure student belongs to the course and semester of the subject
                    if student.course != subject.semester.course or student.current_semester != subject.semester.semester_number:
                        continue
                except StudentProfile.DoesNotExist:
                    continue
                
                Attendance.objects.update_or_create(
                    student=student,
                    subject=subject,
                    date=date_str,
                    defaults={'status': value}
                )
                count += 1
        
        messages.success(request, f'Attendance updated for {count} students.')
        return redirect(f"{request.path}?course={selected_course_id}&semester={selected_semester_id}&subject={selected_subject_id}")

    # GET request: Show form with 3-Level Hierarchical Selection
    # Get all unique courses assigned to faculty
    courses = Course.objects.filter(semesters__subjects__faculty=faculty).distinct()

    selected_course_id = request.GET.get('course')
    selected_semester_id = request.GET.get('semester')
    selected_subject_id = request.GET.get('subject')

    semesters_in_course = []
    subjects_in_semester = []
    students = []
    
    if selected_course_id:
        semesters_in_course = Semester.objects.filter(course_id=selected_course_id, subjects__faculty=faculty).distinct()
        
        if selected_semester_id:
            subjects_in_semester = assigned_subjects.filter(semester_id=selected_semester_id)
            
            if selected_subject_id:
                try:
                    subject = subjects_in_semester.get(id=selected_subject_id)
                    students = StudentProfile.objects.filter(
                        course=subject.semester.course, 
                        current_semester=subject.semester.semester_number
                    ).order_by('roll_number')
                except Subject.DoesNotExist:
                    selected_subject_id = None
        
    context = {
        'courses': courses,
        'selected_course_id': int(selected_course_id) if selected_course_id and selected_course_id.isdigit() else None,
        'semesters': semesters_in_course,
        'selected_semester_id': int(selected_semester_id) if selected_semester_id and selected_semester_id.isdigit() else None,
        'subjects': subjects_in_semester,
        'selected_subject_id': int(selected_subject_id) if selected_subject_id and selected_subject_id.isdigit() else None,
        'students': students,
        'faculty': faculty
    }
    return render(request, 'faculty_dashboard/add_attendance.html', context)

@login_required
def faculty_add_marks(request):
    try:
        faculty = FacultyProfile.objects.get(user=request.user)
    except FacultyProfile.DoesNotExist:
        return redirect('home')

    # Show only subjects assigned to this faculty
    assigned_subjects = Subject.objects.filter(faculty=faculty).select_related('semester__course')

    # Get all unique courses assigned to faculty
    courses = Course.objects.filter(semesters__subjects__faculty=faculty).distinct()
    
    # Initialize from POST/GET
    selected_course_id = request.POST.get('course') or request.GET.get('course')
    selected_semester_id = request.POST.get('semester') or request.GET.get('semester')
    selected_subject_id = request.POST.get('subject') or request.GET.get('subject')
    mark_type = request.POST.get('mark_type') or request.GET.get('mark_type')

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'save_marks':
            subject_id = request.POST.get('subject')
            mark_type = request.POST.get('mark_type')
            
            # Validate subject
            subject = get_object_or_404(assigned_subjects, id=subject_id)
            
            count = 0
            with transaction.atomic():
                for key, value in request.POST.items():
                    if key.startswith('score_'):
                        student_id = key.split('_')[1]
                        score = value
                        
                        if score: # Only save if score is entered
                            try:
                                student = StudentProfile.objects.get(user__id=student_id)
                                
                                # Security check: Ensure student belongs to the course of the subject
                                if student.course != subject.semester.course:
                                    continue
                                
                                InternalMark.objects.update_or_create(
                                    student=student,
                                    subject=subject,
                                    mark_type=mark_type,
                                    defaults={
                                        'score': score, 
                                        'faculty': faculty, 
                                        'is_verified': True 
                                    }
                                )
                                count += 1
                            except StudentProfile.DoesNotExist:
                                continue
            
            messages.success(request, f'Marks updated for {count} students.')
            return redirect(f"{request.path}?course={selected_course_id}&semester={selected_semester_id}&subject={subject_id}&mark_type={mark_type}")

    students = []
    existing_marks = {}
    semesters_in_course = []
    subjects_in_semester = []

    if selected_course_id:
        semesters_in_course = Semester.objects.filter(course_id=selected_course_id, subjects__faculty=faculty).distinct()
        
        if selected_semester_id:
            subjects_in_semester = assigned_subjects.filter(semester_id=selected_semester_id)
            
            if selected_subject_id:
                try:
                    subject = subjects_in_semester.get(id=selected_subject_id)
                    # Relaxed filtering: Any student in this course who is at or beyond this semester
                    students = StudentProfile.objects.filter(
                        course=subject.semester.course,
                        current_semester__gte=subject.semester.semester_number
                    ).order_by('roll_number')
                    
                    if mark_type:
                        marks = InternalMark.objects.filter(subject=subject, mark_type=mark_type)
                        for m in marks:
                            existing_marks[m.student.user.id] = float(m.score)
                except Subject.DoesNotExist:
                    selected_subject_id = None

    context = {
        'courses': courses,
        'selected_course_id': int(selected_course_id) if selected_course_id and str(selected_course_id).isdigit() else None,
        'semesters': semesters_in_course,
        'selected_semester_id': int(selected_semester_id) if selected_semester_id and str(selected_semester_id).isdigit() else None,
        'subjects': subjects_in_semester,
        'selected_subject_id': int(selected_subject_id) if selected_subject_id and str(selected_subject_id).isdigit() else None,
        'students': students,
        'faculty': faculty,
        'mark_choices': InternalMark.MARK_CHOICES,
        'selected_mark_type': mark_type,
        'existing_marks': existing_marks,
    }
    return render(request, 'faculty_dashboard/add_marks.html', context)

@login_required
def faculty_add_notice(request):
    try:
        faculty = FacultyProfile.objects.get(user=request.user)
    except FacultyProfile.DoesNotExist:
        return redirect('home')

    assigned_subjects = Subject.objects.filter(faculty=faculty).select_related('semester__course')

    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        subject_id = request.POST.get('subject')
        is_public = request.POST.get('is_public') == 'on'
        expires_at = request.POST.get('expires_at')
        
        notice = Notice(
            title=title,
            content=content,
            is_public=is_public,
            faculty_posted=faculty
        )
        
        if expires_at:
            notice.expires_at = expires_at
            
        if not is_public and subject_id:
            subject = get_object_or_404(assigned_subjects, id=subject_id)
            notice.subject = subject
            # Also link to course for broad visibility if needed, 
            # but our current filter uses course or subject.
            notice.course = subject.semester.course
            
        notice.save()
        messages.success(request, 'Notice posted successfully.')
        return redirect('faculty_dashboard')

    context = {
        'subjects': assigned_subjects,
        'faculty': faculty
    }
    return render(request, 'faculty_dashboard/add_notice.html', context)