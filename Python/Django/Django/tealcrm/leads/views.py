from typing import Any
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, DeleteView, UpdateView, CreateView, View
from django.urls import reverse_lazy

from team.models import Team
from .models import Lead
from django.contrib import messages

from .forms import AddLeadForm, AddcommentForm
from client.models import Client

# Create your views here.
class LeadListView(ListView):
    model = Lead

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        queryset = super(LeadListView, self).get_queryset()
        queryset = queryset.filter(created_by=self.request.user, converted_to_client=False)
        return queryset
    
class LeadDetailView(DetailView):
    model = Lead

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        context['form'] = AddcommentForm()

    def get_queryset(self) -> QuerySet[Any]:
        queryset = super(LeadDetailView, self).get_queryset()
        return queryset.filter(created_by=self.request.user, pk=self.kwargs.get('pk'))

class LeadDeleteView(DeleteView):
    model = Lead
    success_url = reverse_lazy('leads:list')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self) -> QuerySet[Any]:
        queryset = super(LeadDeleteView, self).get_queryset()
        return queryset.filter(created_by=self.request.user, pk=self.kwargs.get('pk'))
    
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
    
class LeadUpdateView(UpdateView):
    model = Lead
    fields = ('name', 'email', 'description', 'priority', 'status')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self) -> QuerySet[Any]:
        queryset = super(LeadUpdateView, self).get_queryset()
        return queryset.filter(created_by=self.request.user, pk=self.kwargs.get('pk'))
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Lead'
        return context

    def get_success_url(self):
        return reverse_lazy('leads:list')
    
class LeadCreateView(CreateView):
    model = Lead
    fields = ('name', 'email', 'description', 'priority', 'status')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_success_url(self):
        return reverse_lazy('leads:list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        team = Team.objects.filter(created_by=self.request.user)[0]
        context['team'] = team
        context['title'] = 'Add Lead'
        return context
    
    def form_valid(self, form):
        team = Team.objects.filter(created_by=self.request.user)[0]
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.team = team
        self.object.save()
        return redirect(self.get_success_url())
    
class ConvertToClientView(View):
    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        lead = get_object_or_404(Lead, created_by=request.user, pk=pk)
        team = Team.objects.filter(created_by=request.user)[0]
        client = Client.objects.create(
            name = lead.name,
            email = lead.email,
            description = lead.description,
            created_by = request.user,
            team = team,
        )

        lead.converted_to_client = True
        lead.save()

        messages.success(request, 'The lead was converted to a client.')

        return redirect('leads:list')

    
# @login_required
# def leads_detail(request, pk):
#     lead = get_object_or_404(Lead, created_by=request.user, pk=pk)
#     lead = Lead.objects.filter(created_by=request.user).get(pk=pk)
#     return render(request, 'leads/leads_detail.html', {
#         'lead': lead
#     })

# @login_required
# def leads_delete(request, pk):
#     lead = get_object_or_404(Lead, created_by=request.user, pk=pk)
#     lead.delete()
#     messages.success(request, 'The lead was deleted.')
#     return redirect('leads:list')

# @login_required
# def leads_edit(request, pk):
#     lead=get_object_or_404(Lead, created_by=request.user, pk=pk)
#     if request.method == "POST":
#         form = AddLeadForm(request.POST, instance=lead)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'The lead was saved.')
#             return redirect('leads:list')
#     else:
#         form = AddLeadForm(instance=lead)

#     return render(request, 'leads/leads_edit.html', {
#         'form': form
#     })

# @login_required
# def add_lead(request):
#     team = Team.objects.filter(created_by=request.user)[0]

#     if request.method == "POST":
#         form = AddLeadForm(request.POST)
#         if form.is_valid():
#             team = Team.objects.filter(created_by=request.user)[0]
#             lead = form.save(commit=False)
#             lead.created_by = request.user
#             lead.team = team
#             lead.save()
#             messages.success(request, 'The lead was created.')
#             return redirect('dashboard:dashboard')
#     else:
#         form = AddLeadForm()
#     return render(request, 'leads/add_lead.html', {
#         'form': form,
#         'team': team
#     })

# @login_required
# def convert_to_client(request, pk):
#     lead = get_object_or_404(Lead, created_by=request.user, pk=pk)
#     team = Team.objects.filter(created_by=request.user)[0]
#     client = Client.objects.create(
#         name=lead.name,
#         email=lead.email,
#         description=lead.description,
#         created_by=request.user,
#         team=team)
#     lead.converted_to_client = True
#     lead.save()
#     messages.success(request, "The lead was converted to client")
#     return redirect('leads:list')