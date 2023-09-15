from django.urls import path
from . import views

urlpatterns = [
    path('',views.list_patients,name='list_patients')
]
