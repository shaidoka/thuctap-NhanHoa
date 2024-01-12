from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from team.models import Team
from .models import Lead
from django.contrib import messages

from .forms import AddLeadForm
from client.models import Client

# Create your views here.
@login_required
def leads_list(request):
    leads = Lead.objects.filter(created_by=request.user, converted_to_client=False)
    return render(request, 'leads/leads_list.html', {
        'leads': leads
    })

@login_required
def leads_detail(request, pk):
    lead = get_object_or_404(Lead, created_by=request.user, pk=pk)
    lead = Lead.objects.filter(created_by=request.user).get(pk=pk)
    return render(request, 'leads/leads_detail.html', {
        'lead': lead
    })

@login_required
def leads_delete(request, pk):
    lead = get_object_or_404(Lead, created_by=request.user, pk=pk)
    lead.delete()
    messages.success(request, 'The lead was deleted.')
    return redirect('leads_list')

@login_required
def leads_edit(request, pk):
    lead=get_object_or_404(Lead, created_by=request.user, pk=pk)
    if request.method == "POST":
        form = AddLeadForm(request.POST, instance=lead)
        if form.is_valid():
            form.save()
            messages.success(request, 'The lead was saved.')
            return redirect('leads_list')
    else:
        form = AddLeadForm(instance=lead)

    return render(request, 'leads/leads_edit.html', {
        'form': form
    })

@login_required
def add_lead(request):
    team = Team.objects.filter(created_by=request.user)[0]

    if request.method == "POST":
        form = AddLeadForm(request.POST)
        if form.is_valid():
            team = Team.objects.filter(created_by=request.user)[0]
            lead = form.save(commit=False)
            lead.created_by = request.user
            lead.team = team
            lead.save()
            messages.success(request, 'The lead was created.')
            return redirect('dashboard')
    else:
        form = AddLeadForm()
    return render(request, 'leads/add_lead.html', {
        'form': form,
        'team': team
    })

@login_required
def convert_to_client(request, pk):
    lead = get_object_or_404(Lead, created_by=request.user, pk=pk)
    team = Team.objects.filter(created_by=request.user)[0]
    client = Client.objects.create(
        name=lead.name,
        email=lead.email,
        description=lead.description,
        created_by=request.user,
        team=team)
    lead.converted_to_client = True
    lead.save()
    messages.success(request, "The lead was converted to client")
    return redirect('leads_list')