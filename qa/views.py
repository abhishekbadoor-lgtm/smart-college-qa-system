# qa/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from .models import Question, Answer
from users.models import StudentProfile, FacultyProfile


# ============================================
# STUDENT & FACULTY VIEWS
# ============================================

def question_list(request):
    """
    Display list of all questions with search and filter functionality.
    Accessible by students, faculty, and admin.
    """
    # Get student profile for base template
    student = None
    try:
        student = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        pass
    
    questions = Question.objects.all().annotate(answer_count=Count('answers'))
    
    # Search functionality
    search_query = request.GET.get('q', '')
    if search_query:
        questions = questions.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Department filter
    department_filter = request.GET.get('department', '')
    if department_filter:
        questions = questions.filter(department=department_filter)
    
    # Sort filter
    sort_by = request.GET.get('sort', 'recent')
    if sort_by == 'most_answered':
        questions = questions.order_by('-answer_count', '-created_at')
    elif sort_by == 'unanswered':
        questions = questions.filter(answer_count=0).order_by('-created_at')
    else:  # recent (default)
        questions = questions.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(questions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get department choices for filter dropdown
    department_choices = Question.DEPARTMENT_CHOICES
    
    context = {
        'student': student,
        'page_obj': page_obj,
        'search_query': search_query,
        'department_filter': department_filter,
        'sort_by': sort_by,
        'department_choices': department_choices,
    }
    return render(request, 'qa/question_list.html', context)


def question_detail(request, pk):
    """
    Display a single question with all its answers.
    """
    # Get student profile for base template
    student = None
    try:
        student = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        pass
    
    question = get_object_or_404(Question, pk=pk)
    answers = question.answers.all().select_related('user')
    
    context = {
        'student': student,
        'question': question,
        'answers': answers,
    }
    return render(request, 'qa/question_detail.html', context)


@login_required
def ask_question(request):
    """
    Form for students/faculty to ask a new question.
    """
    # Get student profile for base template
    student = None
    try:
        student = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        pass
    
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        department = request.POST.get('department', 'GEN')
        
        if not title or not description:
            messages.error(request, 'Please provide both title and description.')
            return redirect('qa_ask')
        
        Question.objects.create(
            title=title,
            description=description,
            user=request.user,
            department=department
        )
        
        messages.success(request, 'Your question has been posted successfully!')
        return redirect('qa_list')
    
    department_choices = Question.DEPARTMENT_CHOICES
    context = {
        'student': student,
        'department_choices': department_choices
    }
    return render(request, 'qa/ask_question.html', context)


@login_required
def submit_answer(request, pk):
    """
    POST endpoint to submit an answer to a question.
    """
    if request.method != 'POST':
        return redirect('qa_detail', pk=pk)
    
    question = get_object_or_404(Question, pk=pk)
    answer_text = request.POST.get('answer_text', '').strip()
    
    if not answer_text:
        messages.error(request, 'Please provide an answer.')
        return redirect('qa_detail', pk=pk)
    
    Answer.objects.create(
        question=question,
        answer_text=answer_text,
        user=request.user
    )
    
    messages.success(request, 'Your answer has been posted successfully!')
    return redirect('qa_detail', pk=pk)


# ============================================
# FACULTY-ONLY VIEWS
# ============================================

@login_required
def verify_answer(request, pk):
    """
    Faculty or admin can mark an answer as verified/authoritative.
    """
    # Check if user is faculty or admin
    is_faculty = hasattr(request.user, 'facultyprofile')
    is_admin = request.user.is_superuser
    
    if not (is_faculty or is_admin):
        messages.error(request, 'Only faculty and admin can verify answers.')
        return redirect('qa_list')
    
    answer = get_object_or_404(Answer, pk=pk)
    answer.is_verified = not answer.is_verified  # Toggle verification
    answer.save()
    
    status = "verified" if answer.is_verified else "unverified"
    messages.success(request, f'Answer marked as {status}.')
    return redirect('qa_detail', pk=answer.question.pk)


# ============================================
# ADMIN-ONLY VIEWS (in custom_admin app)
# ============================================

# ============================================
# CHATBOT VIEWS
# ============================================

def chat_view(request):
    """
    Renders the main chat interface.
    """
    from .models import ChatMessage

    # Get student profile for base template (if logged in)
    student = None
    chat_history = []
    
    if request.user.is_authenticated:
        try:
            student = StudentProfile.objects.get(user=request.user)
        except StudentProfile.DoesNotExist:
            pass
            
        # Load chat history for authenticated user
        chat_history = ChatMessage.objects.filter(user=request.user).order_by('timestamp')
        
    context = {
        'student': student,
        'chat_history': chat_history,
    }
    return render(request, 'qa/chat.html', context)


def get_bot_response(request):
    """
    API endpoint to handle chat messages.
    """
    from django.http import JsonResponse
    from .models import ChatbotKnowledgeBase, ChatMessage
    import json
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').strip().lower()
            
            if not user_message:
                return JsonResponse({'error': 'Empty message'}, status=400)
            
            # Save user message
            ChatMessage.objects.create(
                user=request.user if request.user.is_authenticated else None,
                message=user_message,
                is_bot=False
            )
            
            # Logic to find answer
            # 1. Exact/Contains match in KnowledgeBase
            # Simple implementation: check if any keyword is in the message
            rules = ChatbotKnowledgeBase.objects.all()
            response_text = "I'm sorry, I cannot understand your question. Please contact the admin or try asking differently."
            
            # Sort rules by length of keyword (descending) to match specific phrases first
            sorted_rules = sorted(rules, key=lambda r: len(r.keyword), reverse=True)
            
            for rule in sorted_rules:
                if rule.keyword.lower() in user_message:
                    response_text = rule.answer
                    break
            
            # Save bot response
            ChatMessage.objects.create(
                user=request.user if request.user.is_authenticated else None,
                message=response_text,
                is_bot=True
            )
            
            return JsonResponse({'response': response_text})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
            
    return JsonResponse({'error': 'Invalid request'}, status=400)



@login_required
def clear_chat(request):
    """
    Clears the chat history for the logged-in user.
    """
    from .models import ChatMessage
    from django.http import JsonResponse
    
    if request.method == 'POST':
        ChatMessage.objects.filter(user=request.user).delete()
        return JsonResponse({'status': 'success', 'message': 'Chat history cleared'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)
