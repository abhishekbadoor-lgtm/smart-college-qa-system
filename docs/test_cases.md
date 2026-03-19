# Smart College QA - Test Cases Documentation

This document contains detailed test cases for the Smart College management system, organized by module.

## 1. Authentication & Authorization
| Test Case ID | Feature | Test Description | Steps | Test Data | Expected Result |
|--------------|---------|------------------|-------|-----------|-----------------|
| AUTH-001 | Student Registration | Register as a new student with valid data. | 1. Navigate to Registration page.<br>2. Fill in Roll Number, Username, Email, and Password.<br>3. Select "Student" role and click Register. | Roll No: `2024MCA01`, Username: `rahul123`, Email: `rahul@gmail.com` | Account created; redirected to verification or login. |
| AUTH-002 | Faculty Registration | Register as a new faculty with valid data. | 1. Register as Faculty with Employee ID and Department.<br>2. Attempt to login immediately after registration. | Emp ID: `FAC005`, Dept: `Information Technology` | Account created; status set to "unverified" for admin approval. Login fails with "Your account is pending admin verification." |
| AUTH-003 | Login | Login with valid student credentials. | 1. Enter student username and password on login page.<br>2. Click Login. | Valid student credentials | Redirected to Student Dashboard. |
| AUTH-004 | Login | Login with valid faculty credentials. | 1. Enter verified faculty username and password on login page.<br>2. Click Login. | Verified faculty credentials | Redirected to Faculty Dashboard. |
| AUTH-005 | Security | Access faculty dashboard as a student. | 1. Login as a Student.<br>2. Manually enter the URL for the Faculty Dashboard (`/faculty/dashboard/`). | N/A | Access denied (403 Forbidden). |
| AUTH-006 | Login | Login with invalid credentials. | 1. Enter incorrect password for a valid user.<br>2. Click Login. | Correct Username, Wrong Password | Error message "Invalid username or password" shown. |
| AUTH-007 | Logout | Click logout button. | 1. Click the "Logout" button from any dashboard. | N/A | Session terminated; redirected to Home/Login page. |

## 2. Student Module
| Test Case ID | Feature | Test Description | Steps | Expected Result |
|--------------|---------|------------------|-------|-----------------|
| STU-001 | Dashboard | View student dashboard after login. | 1. Login as a student.<br>2. Observe dashboard widgets. | Personal info, attendance summary, and latest notices visible. |
| STU-002 | Attendance | View attendance records. | 1. Click on "Attendance" in the sidebar. | List of subjects and attendance percentages displayed correctly. |
| STU-003 | Marks | View internal marks. | 1. Click on "Marks/Results" in the sidebar. | Subject-wise marks displayed after being updated by faculty. |
| STU-004 | Profile | Edit student profile details. | 1. Go to "Profile" -> "Edit Profile".<br>2. Change phone number or address.<br>3. Click Save. | Changes saved successfully in the database. |
| STU-005 | Feedback | Submit feedback for a faculty. | 1. Go to "Feedback".<br>2. Select Faculty, write message and submit. | Feedback submitted; visible to the respective faculty member. |

## 3. Faculty Module
| Test Case ID | Feature | Test Description | Steps | Expected Result |
|--------------|---------|------------------|-------|-----------------|
| FAC-001 | Verification | Access dashboard before admin verification. | 1. Try to access faculty dashboard with an unverified account. | Restricted access message shown. |
| FAC-002 | Attendance | Mark attendance for a class. | 1. Select "Mark Attendance".<br>2. Choose Subject, Date, and Mark P/A for each student.<br>3. Click Save. | Attendance data saved for the selected date and subject. |
| FAC-003 | Marks | Add internal marks for students. | 1. Select "Update Marks".<br>2. Choose Mark Type (Assignment, Quiz, etc.) and enter scores.<br>3. Click Save. | Marks updated for all students in the selected course/subject. |
| FAC-004 | Notices | Post a new notice for students. | 1. Go to "Notices" -> "Post New".<br>2. Fill in details and select target course/subject. | Notice appears on student dashboards. |
| FAC-005 | Feedback | View and reply to student feedback. | 1. View "Recieved Feedback".<br>2. Type a reply in the response field and click "Send". | Faculty can see student reviews and provide a response. |

## 4. Admin Management (Custom Admin)
| Test Case ID | Feature | Test Description | Steps | Expected Result |
|--------------|---------|------------------|-------|-----------------|
| ADM-001 | Faculty Approval | Verify or delete a newly registered faculty. | 1. Go to "Faculty Profiles".<br>2. Click "Verify" on a pending profile. | Faculty status updated; login enabled. |
| ADM-002 | Student Mgmt | Add/Edit/Delete student records. | 1. Use the Admin Panel to search and modify a student record. | Changes reflected across searching and list views. |
| ADM-003 | Course Mgmt | Add a new course with semesters and subjects. | 1. "Add Course" -> "Add Semesters" -> "Add Subjects". | Course structure created successfully. |
| ADM-004 | Chatbot KB | Bulk upload/Add chatbot response rules. | 1. Go to Chatbot Settings.<br>2. Add a new Trigger Keyword and Answer. | Knowledge base updated with new Q&A pairs. |

## 5. Q&A Discussion Forum & Chatbot
| Test Case ID | Feature | Test Description | Steps | Expected Result |
|--------------|---------|------------------|-------|-----------------|
| QA-001 | Ask Question | Post a new question on the forum. | 1. "Ask Question" -> Fill Title/Body.<br>2. Click Post. | Question visible to other students and faculty. |
| QA-002 | Answer | Submit an answer to a question. | 1. Open an existing question.<br>2. Type your response and click "Submit Answer". | Answer appears under the question; author is credited. |
| QA-003 | Verify Answer | Faculty marks an answer as "Verified". | 1. As Faculty, view an answer.<br>2. Click the "Verify" button. | Answer highlighted as "Verified" or "Correct". |
| QA-004 | Chatbot | Ask a question to the AI Bot. | 1. Open Chatbot.<br>2. Type "Exam dates" or any keyword in KB. | Bot provides a relevant response from the knowledge base. |
| QA-005 | Clear Chat | Clear the current chatbot session. | 1. Click "Clear Chat" in the bot interface. | Chat history cleared for the user. |
