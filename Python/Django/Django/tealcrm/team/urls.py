from django.urls import path
from . import views

app_name = 'team'

urlpatterns = [
    path('<int:pk>/edit/', views.edit_team, name='edit'),
    path('<int:pk>/', views.detail, name='detail'),   
]
