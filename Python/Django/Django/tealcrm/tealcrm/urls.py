from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views

from core.views import index, about

urlpatterns = [
    path('', index, name='index'),
    path('dashboard/leads/', include('leads.urls')),
    path('dashboard/clients/', include('client.urls')),
    path('dashboard/', include('userprofile.urls')),
    path('dashboard/teams/', include('team.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('about/', about, name='about'),
    path('login/', views.LoginView.as_view(template_name='userprofile/login.html'), name='login'),
    path('log-out/', views.LogoutView.as_view(), name='logout'),
    path('admin/', admin.site.urls),
]