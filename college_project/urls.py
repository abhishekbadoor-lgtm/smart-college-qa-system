# college_project/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Customize admin site
admin.site.site_header = "Smart College Administration"
admin.site.site_title = "Smart College Admin"
admin.site.index_title = "Welcome to Smart College Admin Dashboard"

urlpatterns = [
    # 1. ADMIN URL (The Admin Login)
    path('admin/', admin.site.urls),
    
    # 2. USERS/AUTH URLs (Django's built-in login/logout)
    # We prefix with 'accounts/' for convention
    path('accounts/', include('django.contrib.auth.urls')), 

    # 3. APP URLs (Student/Faculty registration, main pages)
    path('', include('core.urls')), 
    path('users/', include('users.urls')), # For custom registration views
    path('qa/', include('qa.urls')), # Q&A Discussion Forum
    path('custom-admin/', include('custom_admin.urls')), # Custom Admin Dashboard
    path('cms/', include('cms.urls')), # CMS (Attendance, Marks, etc.)

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# NOTE: The static files line is necessary to serve static files in development
# if we were to upload media (like profile pictures), we'd need a similar line for MEDIA_URL.