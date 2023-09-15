from django.urls import path
from .views import (HomeView, ThankYouView, ContactFormView, 
                    TeacherCreateView, TeacherListView,
                    TeacherDetailView)

app_name = "classroom"

urlpatterns = [
    path('', HomeView.as_view(), name="home"),
    path('thanks/', ThankYouView.as_view(), name='thanks'),
    path('contact/', ContactFormView.as_view(), name='contact'),
    path('create_teacher/', TeacherCreateView.as_view(), name='create_teacher'),
    path('teacher_detail/<int:pk>', TeacherDetailView.as_view(), name="list_teacher"),
    path('list_teacher/', TeacherListView.as_view(), name="list_teacher")
]   

