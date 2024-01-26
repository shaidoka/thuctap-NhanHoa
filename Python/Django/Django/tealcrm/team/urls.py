from django.urls import path
from . import views

app_name = 'team'

urlpatterns = [
    path('<int:pk>/', views.detail, name='detail'),
    path('<int:pk>/edit/', views.edit_team, name='edit'),
    path('', views.team_list, name='list'),
    path('<int:pk>/activate/', views.teams_activate, name='activate')
]
