from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Course, Semester, Subject, Attendance, Feedback
from users.models import FacultyProfile, StudentProfile
from django.utils import timezone
from django.db.models import Q
import datetime

# Helper to check if user is faculty
def is_faculty(user):
    return user.is_authenticated and hasattr(user, 'facultyprofile') and user.facultyprofile.is_verified

def is_student(user):
    return user.is_authenticated and hasattr(user, 'studentprofile') and user.studentprofile.is_verified

@login_required
@user_passes_test(is_faculty)
def mark_attendance(request):
    """
    View for faculty to mark attendance for a course.
    Steps:
    1. Select Course and Date.
    2. List all students in that course (or all students if courses aren't strictly enrolled yet).
    3. Submit attendance.
    """
    faculty = request.user.facultyprofile
    dept = faculty.department
    
    assigned_subjects = Subject.objects.filter(faculty=faculty).select_related('semester__course')
    
    selected_subject_id = request.GET.get('subject')
    selected_date_str = request.GET.get('date') or timezone.now().date().strftime('%Y-%m-%d')
    
    students = []
    
    if selected_subject_id:
        subject = get_object_or_404(assigned_subjects, id=selected_subject_id)
        students = StudentProfile.objects.filter(
            course=subject.semester.course, 
            current_semester=subject.semester.semester_number,
            is_verified=True
        ).select_related('user')
        
        if request.method == 'POST':
            # Processing attendance
            date_obj = datetime.datetime.strptime(selected_date_str, '%Y-%m-%d').date()
            
            # Prevent marking attendance for future dates
            if date_obj > timezone.now().date():
                 messages.error(request, "You cannot mark attendance for future dates.")
                 from django.urls import reverse
                 return redirect(reverse('mark_attendance') + f'?subject={subject.id}&date={selected_date_str}')
            
            for student in students:
                status = request.POST.get(f'status_{student.user.id}')
                if status:
                    Attendance.objects.update_or_create(
                        student=student,
                        subject=subject,
                        date=date_obj,
                        defaults={'status': status}
                    )
            
            messages.success(request, f"Attendance marked for {subject.name} on {selected_date_str}")
            from django.urls import reverse
            return redirect(reverse('mark_attendance') + f'?subject={subject.id}&date={selected_date_str}')

    else:
        subject = None

    # Fetch existing attendance
    existing_attendance = {}
    if subject:
        date_obj = datetime.datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        records = Attendance.objects.filter(subject=subject, date=date_obj)
        for record in records:
            existing_attendance[record.student.user.id] = record.status

    context = {
        'subjects': assigned_subjects,
        'selected_subject': subject,
        'selected_date': selected_date_str,
        'students': students,
        'existing_attendance': existing_attendance,
        'today': timezone.now().date().strftime('%Y-%m-%d'),
    }
    return render(request, 'cms/mark_attendance.html', context)

@login_required
@user_passes_test(is_faculty)
def add_marks(request):
    """
    View for faculty to add internal marks.
    """
    from .models import InternalMark
    
    faculty = request.user.facultyprofile
    dept = faculty.department
    
    assigned_subjects = Subject.objects.filter(faculty=faculty).select_related('semester__course')
    
    selected_subject_id = request.GET.get('subject')
    mark_type = request.GET.get('mark_type') or request.POST.get('mark_type')
    
    students = []
    
    if selected_subject_id:
        subject = get_object_or_404(assigned_subjects, id=selected_subject_id)
        students = StudentProfile.objects.filter(
            course=subject.semester.course, 
            current_semester=subject.semester.semester_number,
            is_verified=True
        ).select_related('user')
        
        if request.method == 'POST':
            if not mark_type:
                messages.error(request, "Please select a mark type.")
            else:
                count = 0
                for student in students:
                    score_str = request.POST.get(f'score_{student.user.id}')
                    if score_str:
                        try:
                            score = float(score_str)
                            InternalMark.objects.update_or_create(
                                student=student,
                                subject=subject,
                                mark_type=mark_type,
                                defaults={'score': score, 'faculty': request.user.facultyprofile}
                            )
                            count += 1
                        except ValueError:
                            continue
                
                if count > 0:
                    messages.success(request, f"Successfully saved {mark_type} marks for {count} students.")
                    from django.urls import reverse
                    return redirect(reverse('add_marks') + f'?subject={subject.id}&mark_type={mark_type}')
                else:
                    messages.warning(request, "No valid scores were entered.")

    else:
        subject = None

    # Fetch existing marks to pre-fill
    existing_marks = {}
    if subject and mark_type:
        marks = InternalMark.objects.filter(subject=subject, mark_type=mark_type)
        for m in marks:
            existing_marks[m.student.user.id] = m.score

    context = {
        'subjects': assigned_subjects,
        'selected_subject': subject,
        'students': students,
        'mark_choices': InternalMark.MARK_CHOICES,
        'selected_mark_type': mark_type,
        'existing_marks': existing_marks,
    }
    return render(request, 'cms/add_marks.html', context)
@login_required
@user_passes_test(is_student)
def student_feedback_create(request):
    """
    View for students to submit feedback to Admin or Faculty.
    """
    student = request.user.studentprofile
    if request.method == 'POST':
        recipient_type = request.POST.get('recipient_type')
        faculty_id = request.POST.get('faculty')
        message_text = request.POST.get('message')
        
        feedback = Feedback(
            student=student,
            name=request.user.get_full_name() or request.user.username,
            email=request.user.email,
            recipient_type=recipient_type,
            message=message_text
        )
        
        if recipient_type == 'FACULTY' and faculty_id:
            feedback.faculty = get_object_or_404(FacultyProfile, user_id=faculty_id)
            
        feedback.save()
        messages.success(request, "Feedback submitted successfully!")
        return redirect('student_feedback_list')
        
    faculties = FacultyProfile.objects.filter(is_verified=True)
    return render(request, 'cms/student_feedback_form.html', {
        'faculties': faculties,
        'student': student
    })

@login_required
@user_passes_test(is_student)
def student_feedback_list(request):
    """
    View for students to see their own feedback and replies.
    """
    student = request.user.studentprofile
    feedbacks = Feedback.objects.filter(student=student).order_by('-date_submitted')
    return render(request, 'cms/student_feedback_list.html', {
        'feedbacks': feedbacks,
        'student': student
    })

@login_required
@user_passes_test(is_faculty)
def faculty_feedback_list(request):
    """
    View for faculty to see feedback directed to them.
    """
    faculty = request.user.facultyprofile
    feedbacks = Feedback.objects.filter(faculty=faculty, recipient_type='FACULTY').order_by('-date_submitted')
    return render(request, 'cms/faculty_feedback_list.html', {
        'feedbacks': feedbacks,
        'faculty': faculty
    })

@login_required
@user_passes_test(is_faculty)
def faculty_feedback_reply(request, pk):
    """
    View for faculty to reply to feedback.
    """
    faculty = request.user.facultyprofile
    feedback = get_object_or_404(Feedback, pk=pk, faculty=faculty, recipient_type='FACULTY')
    
    if request.method == 'POST':
        reply_text = request.POST.get('reply')
        if reply_text:
            feedback.reply = reply_text
            feedback.replied_at = timezone.now()
            feedback.save()
            messages.success(request, "Reply sent successfully!")
            return redirect('faculty_feedback_list')
            
    return render(request, 'cms/faculty_feedback_reply.html', {
        'feedback': feedback,
        'faculty': faculty
    })
