from django.shortcuts import render
from django.views.generic import (TemplateView, FormView, CreateView
                                  , ListView, DetailView, UpdateView,
                                  DeleteView)
from .forms import ContactForm
from django.urls import reverse, reverse_lazy
from classroom.models import Teacher

# Create your views here.
def home_view(request):
    return render(request, 'classroom/home.html')

class HomeView(TemplateView):
    template_name = 'classroom/home.html'

class ThankYouView(TemplateView):
    template_name = 'classroom/thanks.html'

class TeacherCreateView(CreateView):
    model = Teacher
    fields = "__all__"
    success_url = reverse_lazy('classroom:thanks')

class ContactFormView(FormView):
    form_class = ContactForm
    template_name = 'classroom/contact.html'
    # URL that you want to redirect to
    # success_url = "/classroom/thanks/"
    success_url = reverse_lazy('classroom:thanks')
    # What to do with form
    #def form_valid(self, form):
    #    print(form.cleaned_data)

        # similar to ContactForm(request.POST)
    #    return super().form_valid(form)

class TeacherListView(ListView):
    model = Teacher
    queryset = Teacher.objects.order_by("first_name")
    context_object_name = "teacher_list"

class TeacherDetailView(DetailView):
    # model should be called model_detail.html
    model = Teacher

class TeacherUpdateView(UpdateView):
    model = Teacher
    fields = "__all__"
    success_url = reverse_lazy('classroom:teacher_list')

class TeacherDeleteView(DeleteView):
    # Form --> Confirm Delete Button
    # default template name:
    # model_confirm_delete.html
    model = Teacher
    success_url = reverse_lazy('classroom:teacher_list')