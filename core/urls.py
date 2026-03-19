from django.urls import path
from .views import home, login_redirect, custom_logout, public_qa


urlpatterns = [
    path('', home, name='home'),
    path('redirect/', login_redirect, name='login_redirect'),
    path('logout/', custom_logout, name='logout'),
    path('qa-public/', public_qa, name='public_qa'),  # Redirect to new QA system
]
