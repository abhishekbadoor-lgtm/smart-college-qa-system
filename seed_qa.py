import os
import django
import sys

# Setup Django environment
sys.path.append(r'c:\W\MCA\s3\MiNOR PROJECT')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_project.settings')
django.setup()

from qa.models import ChatbotKnowledgeBase

# Clear existing simple rules for clean state (optional)
# ChatbotKnowledgeBase.objects.all().delete()

# Add sample rules
rules = [
    {
        'keyword': 'exam',
        'answer': 'The end semester exams are scheduled to start from December 15th. Please check your personalized schedule in the student portal.'
    },
    {
        'keyword': 'fee', 
        'answer': 'Tuition fees must be paid by January 5th. Late fees will apply after this date. You can pay online via the Payments tab.'
    },
    {
        'keyword': 'hostel',
        'answer': 'Hostel applications for next semester are now open. Visit the Warden Office between 10 AM - 4 PM.'
    },
    {
        'keyword': 'result',
        'answer': 'Last semester results have been declared. You can view them in the "Marks" section of your dashboard.'
    },
    {
        'keyword': 'library',
        'answer': 'The central library is open from 8 AM to 8 PM on weekdays and 9 AM to 5 PM on Saturdays.'
    },
    {
        'keyword': 'hello',
        'answer': 'Hello there! How can I help you today? You can ask me about exams, fees, results, or departments.'
    },
    {
        'keyword': 'hi',
        'answer': 'Hi! I am the College QA Bot. How can I assist you?'
    }
]

count = 0
for rule in rules:
    obj, created = ChatbotKnowledgeBase.objects.get_or_create(
        keyword=rule['keyword'],
        defaults={'answer': rule['answer']}
    )
    if created:
        print(f"Added rule: {rule['keyword']}")
        count += 1
    else:
        print(f"Rule already exists: {rule['keyword']}")

print(f"\nSuccessfully added {count} new rules to Knowledge Base.")
