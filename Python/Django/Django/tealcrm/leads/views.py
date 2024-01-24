from typing import Any
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, DeleteView, UpdateView, CreateView, View
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from team.models import Team
from .models import Comment, Lead
from django.contrib import messages

from .forms import AddLeadForm, AddcommentForm, AddFileForm
from client.models import Client, Comment as ClientComment

# Create your views here.
class LeadListView(LoginRequiredMixin, ListView):
    model = Lead

    def get_queryset(self) -> QuerySet[Any]:
        queryset = super(LeadListView, self).get_queryset()
        return queryset.filter(created_by=self.request.user, converted_to_client=False)
    
class LeadDetailView(LoginRequiredMixin, DetailView):
    model = Lead
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lead'] = self.get_object()
        context['form'] = AddcommentForm()
        context['fileform'] = AddFileForm()
        return context
    
    def get_object(self):
        id = self.kwargs.get("pk")
        lead = Lead.objects.get(id=id)
        return lead

    # def get_queryset(self) -> QuerySet[Any]:
    #     queryset = super(LeadDetailView, self).get_queryset()
    #     return queryset.filter(created_by=self.request.user, pk=self.kwargs.get('pk'))

class LeadDeleteView(LoginRequiredMixin, DeleteView):
    model = Lead
    
    def get_queryset(self) -> QuerySet[Any]:
        queryset = super(LeadDeleteView, self).get_queryset()
        return queryset.filter(created_by=self.request.user, pk=self.kwargs.get('pk'))
    
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
    
    def get_success_url(self):
        return reverse_lazy('leads:list')
    
class LeadUpdateView(LoginRequiredMixin, UpdateView):
    model = Lead
    fields = ('name', 'email', 'description', 'priority', 'status')
    
    def get_queryset(self) -> QuerySet[Any]:
        queryset = super(LeadUpdateView, self).get_queryset()
        return queryset.filter(created_by=self.request.user, pk=self.kwargs.get('pk'))
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Lead'
        return context

    def get_success_url(self):
        return reverse_lazy('leads:list')
    
class LeadCreateView(LoginRequiredMixin, CreateView):
    model = Lead
    fields = ('name', 'email', 'description', 'priority', 'status')
    
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
    
class ConvertToClientView(LoginRequiredMixin, View):
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

        # Convert lead comments to client comments

        comments = lead.comments.all()

        for comment in comments:
            ClientComment.objects.create(
                content = comment.content,
                client = client,
                created_by = comment.created_by,
                team = team
            )
        
        # Show message and redirect

        messages.success(request, 'The lead was converted to a client.')

        return redirect('leads:list')
    
class AddCommentView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        form = AddcommentForm(request.POST)
        if form.is_valid():
            team = Team.objects.filter(created_by=self.request.user)[0]
            comment = form.save(commit=False)
            comment.team = team
            comment.created_by = request.user
            comment.lead_id = pk
            comment.save()

        return redirect('leads:detail', pk=pk)
    
class AddFileView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        form = AddFileForm(request.POST, request.FILES)

        if form.is_valid():
            team = Team.objects.filter(created_by=self.request.user)[0]
            file = form.save(commit=False)
            file.team = team
            file.lead_id = pk
            file.created_by = request.user
            file.save()
        return redirect('leads:detail', pk=pk)

    
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