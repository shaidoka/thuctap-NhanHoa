from django.shortcuts import render
from django.http import HttpResponse
from .models import *
from django.views.generic import (CreateView, UpdateView, DeleteView,
                                  DetailView)
from django.contrib.auth.decorators import login_required
# Create your views here.
def index(request):
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    num_instances_avail = BookInstance.objects.filter(status__exact='a').count()
    context = {
        "num_books":num_books,
        "num_instances":num_instances,
        "num_instances_avail":num_instances_avail
    }
    return render(request, 'catalog/index.html', context=context)

class BookCreate(CreateView):
    model = Book
    fields = '__all__'

class BookDetail(DetailView):
    model = Book

@login_required
def my_view(request):
    return render(request, 'catalog/my_view.html')