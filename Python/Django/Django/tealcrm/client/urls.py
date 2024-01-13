from django.urls import path

from . import views

app_name = 'clients'

clients:list

urlpatterns = [
    path('', views.clients_list, name="list"),
    path('<int:pk>/', views.client_detail, name="detail"),
    path('add/', views.add_client, name="add"),
    path('<int:pk>/delete/', views.client_delete, name='delete'),
    path('<int:pk>/edit/', views.client_edit, name="edit"),
]
