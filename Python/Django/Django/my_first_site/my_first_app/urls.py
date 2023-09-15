from django.urls import path
from . import views

app_name = 'my_first_app'

urlpatterns = [
    path('',views.simple_view,name='simple_view'),
    path('<int:num_page>', views.num_page_view),
    #path('<str:topic>', views.news_view,name="topic-page"),
    path('variable/', views.variable_view, name='variable'),
    #path('<int:num1>/<int:num2>', views.add_view),
    path('basehtml', views.base_html)
]

