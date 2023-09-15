from django.http import HttpResponse
from django.shortcuts import render

def home_view(request):
    return HttpResponse("HOME PAGE")

def custom_404_view(request,exception):
    return render(request, "404.html",status=404)