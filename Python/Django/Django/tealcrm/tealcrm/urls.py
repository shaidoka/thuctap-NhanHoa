from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views
from django.conf import settings
from core.views import index, about
from django.conf.urls.static import static
from userprofile.forms import LoginFrom

urlpatterns = [
    path('', index, name='index'),
    path('dashboard/clients/', include('client.urls')),
    path('dashboard/leads/', include('leads.urls')),
    path('dashboard/', include('userprofile.urls')),
    path('dashboard/teams/', include('team.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('about/', about, name='about'),
    path('login/', views.LoginView.as_view(template_name='userprofile/login.html', authentication_form=LoginFrom), name='login'),
    path('log-out/', views.LogoutView.as_view(), name='logout'),
    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)