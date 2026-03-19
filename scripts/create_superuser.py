import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_project.settings')
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
username = 'admin'
email = 'admin@example.com'
password = 'AdminPass123'  # CHANGE THIS after first login
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Superuser '{username}' created with password '{password}'. Please change it immediately.")
else:
    print(f"Superuser '{username}' already exists.")
