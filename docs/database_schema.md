# Smart College QA - Database Schema Documentation

This document lists all the custom database tables (models) used in the project, excluding default Django tables.

## 1. User Management (users app)

### Table: StudentProfile
| Field | Type | Description |
|-------|------|-------------|
| user | OneToOne (User) | Link to Django User model (Primary Key) |
| roll_number | CharField(15) | Unique ID for the student |
| course | ForeignKey (Course) | Course enrolled by the student |
| current_semester | PositiveIntegerField | Current semester of the student |
| timetable_details | TextField | Details of the student's timetable |
| is_verified | BooleanField | Verification status by Admin |

### Table: FacultyProfile
| Field | Type | Description |
|-------|------|-------------|
| user | OneToOne (User) | Link to Django User model (Primary Key) |
| employee_id | CharField(15) | Unique ID for the faculty |
| department | CharField(100) | Department name |
| is_verified | BooleanField | Verification status by Admin |

---

## 2. College Management System (cms app)

### Table: Course
| Field | Type | Description |
|-------|------|-------------|
| name | CharField(100) | Name of the course |
| code | CharField(10) | Unique course code |
| description | TextField | Detailed course description |

### Table: Semester
| Field | Type | Description |
|-------|------|-------------|
| course | ForeignKey (Course) | Parent course |
| semester_number | PositiveIntegerField | Number of the semester |

### Table: Subject
| Field | Type | Description |
|-------|------|-------------|
| semester | ForeignKey (Semester) | Parent semester |
| name | CharField(100) | Subject name |
| code | CharField(20) | Unique subject code |
| faculty | ForeignKey (FacultyProfile) | Assigned faculty |
| description | TextField | Subject description |

### Table: Notice
| Field | Type | Description |
|-------|------|-------------|
| title | CharField(200) | Notice title |
| content | TextField | Notice content |
| date_posted | DateTimeField | Creation timestamp |
| is_public | BooleanField | Visibility to all users |
| course | ForeignKey (Course) | Targeted course (optional) |
| subject | ForeignKey (Subject) | Targeted subject (optional) |
| faculty_posted | ForeignKey (FacultyProfile)| Authoring faculty |
| expires_at | DateTimeField | Expiration date |

### Table: InternalMark
| Field | Type | Description |
|-------|------|-------------|
| student | ForeignKey (StudentProfile)| Target student |
| faculty | ForeignKey (FacultyProfile)| Awarding faculty |
| subject | ForeignKey (Subject) | Subject for the marks |
| mark_type | CharField(2) | Type (Assignment, Quiz, etc.) |
| score | DecimalField(5,2) | Marks obtained |
| date_entered | DateTimeField | Timestamp of entry |
| is_verified | BooleanField | Verification status |

### Table: Feedback
| Field | Type | Description |
|-------|------|-------------|
| student | ForeignKey (StudentProfile)| Submitting student (optional) |
| name | CharField(100) | Name of submitter |
| email | EmailField | Email of submitter |
| recipient_type | CharField(10) | Admin or Faculty |
| faculty | ForeignKey (FacultyProfile)| Target faculty (if applicable) |
| message | TextField | Feedback content |
| date_submitted | DateTimeField | Timestamp |
| reply | TextField | Response from recipient |
| replied_at | DateTimeField | Timestamp of reply |

### Table: Attendance
| Field | Type | Description |
|-------|------|-------------|
| student | ForeignKey (StudentProfile)| Target student |
| subject | ForeignKey (Subject) | Scoped subject |
| date | DateField | Date of attendance |
| status | CharField(1) | P/A/L status |

---

## 3. Q&A and Chatbot (qa app)

### Table: Question
| Field | Type | Description |
|-------|------|-------------|
| title | CharField(255) | Question summary |
| description | TextField | Detailed query |
| user | ForeignKey (User) | Author |
| department | CharField(3) | Selected department |
| is_verified | BooleanField | Admin verification status |
| created_at | DateTimeField | Timestamp |

### Table: Answer
| Field | Type | Description |
|-------|------|-------------|
| question | ForeignKey (Question) | Parent question |
| answer_text | TextField | Content of the answer |
| user | ForeignKey (User) | Author |
| is_verified | BooleanField | Authoritative status |
| created_at | DateTimeField | Timestamp |

### Table: ChatbotKnowledgeBase
| Field | Type | Description |
|-------|------|-------------|
| keyword | CharField(255) | Trigger keyword/question |
| answer | TextField | Automated response |
| department | CharField(3) | Contextual department |

### Table: ChatMessage
| Field | Type | Description |
|-------|------|-------------|
| user | ForeignKey (User) | Chat user |
| message | TextField | Message content |
| is_bot | BooleanField | Sent by system? |
| timestamp | DateTimeField | Timestamp |
