from django.urls import path
from . import views

app_name = 'clients'

urlpatterns = [
    path('', views.clients_list, name="list"),
    path('<int:pk>/', views.client_detail, name="detail"),
    path('add/', views.add_client, name="add"),
    path('<int:pk>/delete/', views.client_delete, name='delete'),
    path('<int:pk>/edit/', views.client_edit, name="edit"),
    path('<int:pk>/add-comment', views.client_detail, name='add_comment'),
    path('<int:pk>/add-file/', views.client_add_file, name='add_file'),
    path('export/', views.clients_export, name='export'),
]