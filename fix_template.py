# Fix template file
content = '''{% extends 'student_dashboard/base.html' %}

{% block title %}Q&A Discussion Forum{% endblock %}

{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4">
    <h4><i class="fas fa-comments me-2"></i>Q&A Discussion Forum</h4>
    <a href="{% url 'qa_ask' %}" class="btn btn-primary">
        <i class="fas fa-plus-circle me-2"></i>Ask Question
    </a>
</div>

<div class="card shadow-sm border-0 mb-4">
    <div class="card-body">
        <p class="text-center">Simple QA System - Working!</p>
        <a href="{% url 'qa_ask' %}" class="btn btn-primary">Ask a Question</a>
    </div>
</div>

{% if page_obj %}
    {% for question in page_obj %}
    <div class="card shadow-sm border-0 mb-3">
        <div class="card-body">
            <h5><a href="{% url 'qa_detail' question.pk %}">{{ question.title }}</a></h5>
            <p class="text-muted small">{{ question.description|truncatewords:30 }}</p>
            <small class="text-muted">{{ question.user.username }} - {{ question.answer_count }} answers</small>
        </div>
    </div>
    {% endfor %}
{% else %}
    <div class="alert alert-info">No questions found. <a href="{% url 'qa_ask' %}">Ask a question!</a></div>
{% endif %}
{% endblock %}'''

with open(r'c:\W\MCA\s3\MiNOR PROJECT\templates\qa\question_list.html', 'w', encoding='utf-8') as f:
    f.write(content)
    
print("Template file updated successfully!")
