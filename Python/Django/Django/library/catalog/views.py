from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse_lazy
from .models import *
from django.views.generic import (CreateView, UpdateView, DeleteView,
                                  DetailView, ListView)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

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

class BookCreate(LoginRequiredMixin, CreateView):
    model = Book
    fields = '__all__'

class BookDetail(DetailView):
    model = Book

@login_required
def my_view(request):
    return render(request, 'catalog/my_view.html')

class SignupView(CreateView):
    form_class = UserCreationForm
    template_name = 'catalog/signup.html'
    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return redirect('/')
    success_url = reverse_lazy('index')

class CheckedOutBooksByUserView(LoginRequiredMixin, ListView):
    # List all BookInstances filtered by currently logged in user
    model = BookInstance
    template_name = 'catalog/profile.html'
    paginate_by = 5 # 5 bookinstances per page
    def get_queryset(self) -> QuerySet[Any]:
        return BookInstance.objects.filter(borrower=self.request.user)