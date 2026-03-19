# Smart College QA - Use Case Diagrams

This document visualizes the interactions between different users (Actors) and the system.

## 1. Student Use Cases
The student interacts with the system to manage their academic journey and use support tools.

```mermaid
useCaseDiagram
    actor Student
    
    package "Smart College System" {
        usecase "Login/Register" as UC1
        usecase "View Personal Dashboard" as UC2
        usecase "Check Attendance" as UC3
        usecase "View Internal Marks" as UC4
        usecase "Read Notices" as UC5
        usecase "Submit Faculty Feedback" as UC6
        usecase "Post/Answer in QA Forum" as UC7
        usecase "Chat with AI Bot" as UC8
    }

    Student --> UC1
    Student --> UC2
    Student --> UC3
    Student --> UC4
    Student --> UC5
    Student --> UC6
    Student --> UC7
    Student --> UC8
```

---

## 2. Faculty Use Cases
The faculty actor manages classroom activities and provides feedback/verification.

```mermaid
useCaseDiagram
    actor Faculty
    
    package "Smart College System" {
        usecase "Login/Register (Pending Verification)" as UC9
        usecase "Manage Class Attendance" as UC10
        usecase "Add/Update Internal Marks" as UC11
        usecase "Post Course/Subject Notices" as UC12
        usecase "View & Reply Student Feedback" as UC13
        usecase "Verify Answers in QA Forum" as UC14
    }

    Faculty --> UC9
    Faculty --> UC10
    Faculty --> UC11
    Faculty --> UC12
    Faculty --> UC13
    Faculty --> UC14
```

---

## 3. High-Level System / Admin Use Cases
The administrator manages the platform's core data and user access.

```mermaid
useCaseDiagram
    actor Administrator
    
    package "Smart College System" {
        usecase "Verify Faculty & Students" as UC15
        usecase "Manage Courses & Subjects" as UC16
        usecase "Announce General Notices" as UC17
        usecase "Moderate QA Forum" as UC18
        usecase "Configure Chatbot Knowledge Base" as UC19
        usecase "Analyze Feedback Reports" as UC20
    }

    Administrator --> UC15
    Administrator --> UC16
    Administrator --> UC17
    Administrator --> UC18
    Administrator --> UC19
    Administrator --> UC20
```
