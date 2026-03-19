import os

path = r'c:/W/MCA/s3/MiNOR PROJECT/templates/cms/mark_attendance.html'

content = """{% extends 'base.html' %}
{% load cms_extras %}

{% block content %}
<div class="row mb-4">
    <div class="col-12">
        <h2 class="text-primary fw-bold">Mark Attendance</h2>
        <p class="text-muted">Select a course and date to manage student attendance.</p>
    </div>
</div>

<div class="card shadow-sm mb-4">
    <div class="card-body">
        <form method="get" class="row g-3 align-items-end">
            <div class="col-md-4">
                <label for="course" class="form-label fw-bold">Select Course</label>
                <select name="course" id="course" class="form-select" onchange="this.form.submit()">
                    <option value="">-- Select Course --</option>
                    {% for c in courses %}
                    <option value="{{ c.id }}" {% if selected_course and selected_course.id == c.id %}selected{% endif %}>
                        {{ c.code }} - {{ c.name }}
                    </option>
                    {% endfor %}
                </select>
            </div>
            <div class="col-md-4">
                <label for="date" class="form-label fw-bold">Select Date</label>
                <input type="date" name="date" id="date" class="form-control" value="{{ selected_date }}"
                    onchange="this.form.submit()">
            </div>
        </form>
    </div>
</div>

{% if selected_course %}
<div class="card shadow-sm">
    <div class="card-header bg-primary text-white">
        <h5 class="mb-0">Attendance for {{ selected_course.name }} ({{ selected_date }})</h5>
    </div>
    <div class="card-body">
        {% if students %}
        <form method="post">
            {% csrf_token %}
            <div class="table-responsive">
                <table class="table table-hover align-middle">
                    <thead class="table-light">
                        <tr>
                            <th>Roll Number</th>
                            <th>Student Name</th>
                            <th class="text-center">Present</th>
                            <th class="text-center">Absent</th>
                            <th class="text-center">Late</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for student in students %}
                        <tr>
                            <td>{{ student.roll_number }}</td>
                            <td>{{ student.user.get_full_name|default:student.user.username }}</td>
                            <td class="text-center">
                                <div class="form-check d-inline-block">
                                    <input class="form-check-input" type="radio" name="status_{{ student.user.id }}" id="status_P_{{ student.user.id }}" value="P" required {% if existing_attendance|get_item:student.user.id == 'P' or not existing_attendance|get_item:student.user.id %}checked{% endif %}>
                                    <label class="form-check-label" for="status_P_{{ student.user.id }}">P</label>
                                </div>
                            </td>
                            <td class="text-center">
                                <div class="form-check d-inline-block">
                                    <input class="form-check-input" type="radio" name="status_{{ student.user.id }}" id="status_A_{{ student.user.id }}" value="A" {% if existing_attendance|get_item:student.user.id == 'A' %}checked{% endif %}>
                                    <label class="form-check-label" for="status_A_{{ student.user.id }}">A</label>
                                </div>
                            </td>
                            <td class="text-center">
                                <div class="form-check d-inline-block">
                                    <input class="form-check-input" type="radio" name="status_{{ student.user.id }}" id="status_L_{{ student.user.id }}" value="L" {% if existing_attendance|get_item:student.user.id == 'L' %}checked{% endif %}>
                                    <label class="form-check-label" for="status_L_{{ student.user.id }}">L</label>
                                </div>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            <div class="mt-3 text-end">
                <button type="submit" class="btn btn-success px-4">Save Attendance</button>
            </div>
        </form>
        {% else %}
        <div class="alert alert-info text-center">
            No verified students found enrolled in this course.
        </div>
        {% endif %}
    </div>
</div>
{% endif %}

{% endblock %}
"""

if os.path.exists(path):
    os.remove(path)
    print("Deleted old file.")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Created new file.")
