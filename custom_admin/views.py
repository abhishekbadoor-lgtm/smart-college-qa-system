from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from users.models import StudentProfile, FacultyProfile
from cms.models import Course, InternalMark, Notice, Feedback, Semester, Subject
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Max
from users.forms import StudentRegistrationForm
import csv
import io

# Check if user is superuser
def is_admin(user):
    return user.is_superuser

@user_passes_test(is_admin)
def dashboard(request):
    # Fetch stats
    total_faculty = FacultyProfile.objects.count()
    total_students = StudentProfile.objects.count()
    total_courses = Course.objects.count()
    
    # Pending verifications
    pending_faculty = FacultyProfile.objects.filter(is_verified=False).count()
    pending_students = StudentProfile.objects.filter(is_verified=False).count()
    total_pending = pending_faculty + pending_students

    context = {
        'total_faculty': total_faculty,
        'total_students': total_students,
        'total_courses': total_courses,
        'total_pending': total_pending,
        'pending_faculty': pending_faculty,
        'pending_students': pending_students,
    }
    return render(request, 'custom_admin/dashboard.html', context)

# ---------------------------------------------------------
# Faculty Management
# ---------------------------------------------------------
@user_passes_test(is_admin)
def faculty_list(request):
    faculty_members = FacultyProfile.objects.all().select_related('user')
    return render(request, 'custom_admin/faculty_list.html', {'faculty_members': faculty_members})

@user_passes_test(is_admin)
def verify_faculty(request, pk):
    faculty = get_object_or_404(FacultyProfile, pk=pk)
    faculty.is_verified = True
    faculty.save()
    messages.success(request, f'Faculty {faculty.user.username} verified successfully.')
    return redirect('admin_faculty_list')

@user_passes_test(is_admin)
def delete_faculty(request, pk):
    faculty = get_object_or_404(FacultyProfile, pk=pk)
    user = faculty.user
    user.delete() # This will cascade delete the profile
    messages.success(request, f'Faculty {user.username} deleted successfully.')
    return redirect('admin_faculty_list')

@user_passes_test(is_admin)
def faculty_detail(request, pk):
    faculty = get_object_or_404(FacultyProfile, pk=pk)
    return render(request, 'custom_admin/faculty_detail.html', {'faculty': faculty})

# ---------------------------------------------------------
# Student Management
# ---------------------------------------------------------
@user_passes_test(is_admin)
def student_list(request):
    students = StudentProfile.objects.all().select_related('user', 'course')
    return render(request, 'custom_admin/student_list.html', {'students': students})

@user_passes_test(is_admin)
def verify_student(request, pk):
    student = get_object_or_404(StudentProfile, pk=pk)
    student.is_verified = True
    student.save()
    messages.success(request, f'Student {student.user.username} verified successfully.')
    return redirect('admin_student_list')

@user_passes_test(is_admin)
def delete_student(request, pk):
    student = get_object_or_404(StudentProfile, pk=pk)
    user = student.user
    user.delete()
    messages.success(request, f'Student {user.username} deleted successfully.')
    return redirect('admin_student_list')

@user_passes_test(is_admin)
def student_detail(request, pk):
    student = get_object_or_404(StudentProfile, pk=pk)
    return render(request, 'custom_admin/student_detail.html', {'student': student})

@user_passes_test(is_admin)
def edit_student(request, pk):
    student = get_object_or_404(StudentProfile, pk=pk)
    courses = Course.objects.all()
    
    if request.method == 'POST':
        student.user.first_name = request.POST.get('first_name')
        student.user.last_name = request.POST.get('last_name')
        student.user.email = request.POST.get('email')
        student.roll_number = request.POST.get('roll_number')
        
        course_id = request.POST.get('course')
        if course_id:
            student.course = Course.objects.get(id=course_id)
            
        student.current_semester = int(request.POST.get('current_semester', 1))
        
        student.user.save()
        student.save()
        messages.success(request, f'Student {student.user.username} updated successfully.')
        return redirect('admin_student_list')
        
    return render(request, 'custom_admin/student_form.html', {
        'student': student,
        'courses': courses
    })

@user_passes_test(is_admin)
def add_student(request):
    """Admin-only view to register a new student account."""
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                # 1. Save the basic User object
                user = form.save()
                user.first_name = form.cleaned_data.get('first_name')
                user.last_name = form.cleaned_data.get('last_name')
                user.email = form.cleaned_data.get('email')
                user.save()

                # 2. Save the StudentProfile object
                StudentProfile.objects.create(
                    user=user,
                    roll_number=form.cleaned_data.get('roll_number'),
                    course=form.cleaned_data.get('course'),
                    is_verified=True # Admins create verified accounts by default
                )
            messages.success(request, f'Student {user.username} registered successfully!')
            return redirect('admin_student_list')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = StudentRegistrationForm()
        
    return render(request, 'custom_admin/student_registration_form.html', {'form': form})

# ---------------------------------------------------------
# Course Management
# ---------------------------------------------------------
@user_passes_test(is_admin)
def course_list(request):
    courses = Course.objects.all()
    return render(request, 'custom_admin/course_list.html', {'courses': courses})

@user_passes_test(is_admin)
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    # Prefetch semesters and their subjects for performance
    semesters = course.semesters.all().prefetch_related('subjects__faculty__user')
    return render(request, 'custom_admin/course_detail.html', {
        'course': course,
        'semesters': semesters
    })

@user_passes_test(is_admin)
def add_course(request):
    faculties = FacultyProfile.objects.filter(is_verified=True).select_related('user')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        
        # Auto-calculate next numeric code starting from 103
        all_codes = Course.objects.values_list('code', flat=True)
        numeric_codes = []
        for c in all_codes:
            if c and c.isdigit():
                numeric_codes.append(int(c))
        
        next_code = 103
        if numeric_codes:
            max_num = max(numeric_codes)
            if max_num >= 103:
                next_code = max_num + 1
        
        code = str(next_code)
        description = request.POST.get('description')
        total_semesters = int(request.POST.get('total_semesters', 0))
        
        try:
            with transaction.atomic():
                course = Course.objects.create(name=name, code=code, description=description)
                
                for i in range(1, total_semesters + 1):
                    semester = Semester.objects.create(course=course, semester_number=i)
                    
                    subject_count = int(request.POST.get(f'semester_{i}_subject_count', 0))
                    for j in range(1, subject_count + 1):
                        sub_name = request.POST.get(f'subject_{i}_{j}_name')
                        sub_code = request.POST.get(f'subject_{i}_{j}_code')
                        sub_faculty_id = request.POST.get(f'subject_{i}_{j}_faculty')
                        sub_desc = request.POST.get(f'subject_{i}_{j}_description', '')
                        
                        if sub_name and sub_code:
                            faculty = None
                            if sub_faculty_id:
                                faculty = FacultyProfile.objects.get(user_id=sub_faculty_id)
                            
                            Subject.objects.create(
                                semester=semester,
                                name=sub_name,
                                code=sub_code,
                                faculty=faculty,
                                description=sub_desc
                            )
                
            messages.success(request, 'Course with semesters and subjects added successfully.')
            return redirect('admin_course_list')
        except Exception as e:
            messages.error(request, f'Error adding course: {str(e)}')
        
    return render(request, 'custom_admin/course_form.html', {'faculties': faculties})

@user_passes_test(is_admin)
def edit_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    faculties = FacultyProfile.objects.filter(is_verified=True).select_related('user')
    
    # Pre-fetch existing structure for the form
    semesters = course.semesters.all().prefetch_related('subjects')
    
    if request.method == 'POST':
        course.name = request.POST.get('name')
        # Code remains the same on edit, based on user's "admin should not add any field" 
        # but we can allow saving if it's already there or handle as read-only in template.
        # course.code = request.POST.get('code') # Removed as per instruction for automatic code handling
        course.description = request.POST.get('description')
        total_semesters = int(request.POST.get('total_semesters', 0))
        
        try:
            with transaction.atomic():
                course.save()
                
                # Simple approach for edit: Clear and rebuild or update existing?
                # Rebuilding is easier but might break references if other models link to Subject/Semester.
                # Since this is a minor project, we can rebuild semesters and subjects.
                course.semesters.all().delete()
                
                for i in range(1, total_semesters + 1):
                    semester = Semester.objects.create(course=course, semester_number=i)
                    
                    subject_count = int(request.POST.get(f'semester_{i}_subject_count', 0))
                    for j in range(1, subject_count + 1):
                        sub_name = request.POST.get(f'subject_{i}_{j}_name')
                        sub_code = request.POST.get(f'subject_{i}_{j}_code')
                        sub_faculty_id = request.POST.get(f'subject_{i}_{j}_faculty')
                        sub_desc = request.POST.get(f'subject_{i}_{j}_description', '')
                        
                        if sub_name and sub_code:
                            faculty = None
                            if sub_faculty_id:
                                faculty = FacultyProfile.objects.get(user_id=sub_faculty_id)
                            
                            Subject.objects.create(
                                semester=semester,
                                name=sub_name,
                                code=sub_code,
                                faculty=faculty,
                                description=sub_desc
                            )
                
            messages.success(request, 'Course updated successfully.')
            return redirect('admin_course_list')
        except Exception as e:
            messages.error(request, f'Error updating course: {str(e)}')
            
    return render(request, 'custom_admin/course_form.html', {
        'course': course, 
        'faculties': faculties,
        'semesters': semesters
    })

@user_passes_test(is_admin)
def delete_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    course.delete()
    messages.success(request, 'Course deleted successfully.')
    return redirect('admin_course_list')

# ---------------------------------------------------------
# Notice Management
# ---------------------------------------------------------
@user_passes_test(is_admin)
def notice_list(request):
    notices = Notice.objects.all().order_by('-date_posted')
    return render(request, 'custom_admin/notice_list.html', {'notices': notices})

@user_passes_test(is_admin)
def add_notice(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        is_public = request.POST.get('is_public') == 'on'
        
        Notice.objects.create(title=title, content=content, is_public=is_public)
        messages.success(request, 'Notice posted successfully.')
        return redirect('admin_notice_list')
        
    return render(request, 'custom_admin/notice_form.html')

@user_passes_test(is_admin)
def delete_notice(request, pk):
    notice = get_object_or_404(Notice, pk=pk)
    notice.delete()
    messages.success(request, 'Notice deleted successfully.')
    return redirect('admin_notice_list')

# ---------------------------------------------------------
# Feedback Management
# ---------------------------------------------------------
@user_passes_test(is_admin)
def feedback_list(request):
    feedbacks = Feedback.objects.filter(recipient_type='ADMIN').order_by('-date_submitted')
    return render(request, 'custom_admin/feedback_list.html', {'feedbacks': feedbacks})

@user_passes_test(is_admin)
def feedback_detail(request, pk):
    from django.utils import timezone
    feedback = get_object_or_404(Feedback, pk=pk)
    
    if request.method == 'POST':
        reply_text = request.POST.get('reply')
        if reply_text:
            feedback.reply = reply_text
            feedback.replied_at = timezone.now()
            feedback.save()
            messages.success(request, 'Reply saved for this feedback.')
            return redirect('admin_feedback_detail', pk=pk)
            
    return render(request, 'custom_admin/feedback_detail.html', {'feedback': feedback})

# ---------------------------------------------------------
# Q&A Management
# ---------------------------------------------------------
@user_passes_test(is_admin)
def qa_list(request):
    from qa.models import Question
    
    questions = Question.objects.all().select_related('user').order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('q', '')
    if search_query:
        from django.db.models import Q
        questions = questions.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Add answer count to each question
    from django.db.models import Count
    questions = questions.annotate(answer_count=Count('answers'))
    
    return render(request, 'custom_admin/qa_list.html', {
        'questions': questions,
        'search_query': search_query
    })

@user_passes_test(is_admin)
def qa_delete_question(request, pk):
    from qa.models import Question
    
    question = get_object_or_404(Question, pk=pk)
    question.delete()
    messages.success(request, 'Question and all its answers deleted successfully.')
    return redirect('admin_qa_list')

@user_passes_test(is_admin)
def qa_delete_answer(request, pk):
    from qa.models import Answer
    
    answer = get_object_or_404(Answer, pk=pk)
    question_pk = answer.question.pk
    answer.delete()
    messages.success(request, 'Answer deleted successfully.')
    return redirect('qa_detail', pk=question_pk)

@user_passes_test(is_admin)
def qa_verify_question(request, pk):
    from qa.models import Question
    
    question = get_object_or_404(Question, pk=pk)
    question.is_verified = not question.is_verified
    question.save()
    
    status = "verified" if question.is_verified else "unverified"
    messages.success(request, f'Question marked as {status}.')
    return redirect('admin_qa_list')


# ---------------------------------------------------------
# Chatbot Knowledge Base Management
# ---------------------------------------------------------
@user_passes_test(is_admin)
def chatbot_list(request):
    from qa.models import ChatbotKnowledgeBase
    
    rules = ChatbotKnowledgeBase.objects.all().order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('q', '')
    if search_query:
        rules = rules.filter(keyword__icontains=search_query)
        
    return render(request, 'custom_admin/chatbot_list.html', {
        'rules': rules,
        'search_query': search_query
    })

@user_passes_test(is_admin)
def add_chatbot_rule(request):
    from qa.models import ChatbotKnowledgeBase
    from qa.models import Question # to access choices
    
    if request.method == 'POST':
        keyword = request.POST.get('keyword')
        answer = request.POST.get('answer')
        department = request.POST.get('department')
        
        ChatbotKnowledgeBase.objects.create(
            keyword=keyword, 
            answer=answer,
            department=department
        )
        messages.success(request, 'New rule added to Knowledge Base.')
        return redirect('admin_chatbot_list')
        
    return render(request, 'custom_admin/chatbot_form.html', {
        'department_choices': Question.DEPARTMENT_CHOICES
    })

@user_passes_test(is_admin)
def edit_chatbot_rule(request, pk):
    from qa.models import ChatbotKnowledgeBase
    from qa.models import Question # to access choices
    
    rule = get_object_or_404(ChatbotKnowledgeBase, pk=pk)
    
    if request.method == 'POST':
        rule.keyword = request.POST.get('keyword')
        rule.answer = request.POST.get('answer')
        rule.department = request.POST.get('department')
        rule.save()
        messages.success(request, 'Rule updated successfully.')
        return redirect('admin_chatbot_list')
        
    return render(request, 'custom_admin/chatbot_form.html', {
        'rule': rule,
        'department_choices': Question.DEPARTMENT_CHOICES
    })

@user_passes_test(is_admin)
def delete_chatbot_rule(request, pk):
    from qa.models import ChatbotKnowledgeBase
    
    rule = get_object_or_404(ChatbotKnowledgeBase, pk=pk)
    rule.delete()
    messages.success(request, 'Rule deleted from Knowledge Base.')
    return redirect('admin_chatbot_list')

@user_passes_test(is_admin)
def bulk_upload_chatbot_rules(request):
    from qa.models import ChatbotKnowledgeBase, Question
    
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Please upload a CSV file.')
            return redirect('admin_chatbot_list')
            
        try:
            decoded_file = csv_file.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)
            
            rules_created = 0
            for row in reader:
                keyword = row.get('keyword', '').strip()
                answer = row.get('answer', '').strip()
                department = row.get('department', 'GEN').strip().upper()
                
                # Validate department choice
                valid_departments = [choice[0] for choice in Question.DEPARTMENT_CHOICES]
                if department not in valid_departments:
                    department = 'GEN'
                
                if keyword and answer:
                    ChatbotKnowledgeBase.objects.create(
                        keyword=keyword,
                        answer=answer,
                        department=department
                    )
                    rules_created += 1
            
            messages.success(request, f'Successfully uploaded {rules_created} rules.')
        except Exception as e:
            messages.error(request, f'Error processing CSV: {str(e)}')
            
        return redirect('admin_chatbot_list')
    
    return redirect('admin_chatbot_list')
