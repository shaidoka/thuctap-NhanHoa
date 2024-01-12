from django.urls import path

from . import views

urlpatterns = [
    path('', views.clients_list, name="clients_list"),
    path('<int:pk>/', views.client_detail, name="client_detail"),
    path('add/', views.add_client, name="add_client"),
    path('<int:pk>/delete/', views.client_delete, name='client_delete'),
    path('<int:pk>/edit/', views.client_edit, name="client_edit"),
]
