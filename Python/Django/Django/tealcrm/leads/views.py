from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Lead
from django.contrib import messages

from .forms import AddLeadForm

# Create your views here.
@login_required
def leads_list(request):
    leads = Lead.objects.filter(created_by=request.user)
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
    if request.method == "POST":
        form = AddLeadForm(request.POST)
        if form.is_valid():
            lead = form.save(commit=False)
            lead.created_by = request.user
            lead.save()
            messages.success(request, 'The lead was created.')
            return redirect('dashboard')
    else:
        form = AddLeadForm()
    return render(request, 'leads/add_lead.html', {
        'form': form
    })