from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.urls import path, include

urlpatterns = [
    path('', lambda r: redirect('objects:map'), name='home'),
    path('admin/', admin.site.urls),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('objects/', include('objects.urls')),
    path('references/', include('references.urls')),
]
