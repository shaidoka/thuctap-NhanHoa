from django.urls import path
from .views import (HomeView, ThankYouView, ContactFormView, 
                    TeacherCreateView, TeacherListView,
                    TeacherDetailView, TeacherUpdateView,
                    TeacherDeleteView)

app_name = "classroom"

urlpatterns = [
    path('', HomeView.as_view(), name="home"),
    path('thanks/', ThankYouView.as_view(), name='thanks'),
    path('contact/', ContactFormView.as_view(), name='contact'),
    path('create_teacher/', TeacherCreateView.as_view(), name='create_teacher'),
    path('teacher_detail/<int:pk>', TeacherDetailView.as_view(), name="detail_teacher"),
    path('teacher_list/', TeacherListView.as_view(), name="teacher_list"),
    path('update_teacher/<int:pk>', TeacherUpdateView.as_view(), name='update_teacher'),
    path('delete_teacher/<int:pk>', TeacherDeleteView.as_view(), name="delete_teacher")
]   

