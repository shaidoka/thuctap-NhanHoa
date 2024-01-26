from django.shortcuts import render, get_object_or_404, redirect

from team.models import Team
from .models import Client
from django.contrib.auth.decorators import login_required
from .forms import *
from django.contrib import messages
from django.http import HttpResponse
import csv

# Create your views here.
@login_required
def clients_export(request):
    clients = Client.objects.filter(created_by=request.user)
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="clients.csv"'},
    )

    writer = csv.writer(response)
    writer.writerow(['Client', 'Description', 'Created at', 'Created by'])

    for client in clients:
        writer.writerow([client.name, client.description, client.created_at, client.created_by])

    return response

@login_required
def clients_list(request):
    clients = Client.objects.filter(created_by=request.user)
    return render(request, 'client/clients_list.html', {
        'clients': clients
    })

@login_required
def client_add_file(request, pk):
    client = get_object_or_404(Client, created_by=request.user, pk=pk)

    if request.method == "POST":
        form = AddFileForm(request.POST, request.FILES)

        if form.is_valid():
            file = form.save(commit=False)
            file.team = request.user.userprofile.active_team
            file.client_id = pk
            file.created_by = request.user
            file.save()
            return redirect('clients:detail', pk=pk)

    return redirect('clients:detail', pk=pk)


@login_required
def client_detail(request, pk):
    client = get_object_or_404(Client, created_by=request.user, id=pk)
    
    if request.method == 'POST':
        form = AddCommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.team = request.user.userprofile.active_team
            comment.created_by = request.user
            comment.client = client
            comment.save()

            return redirect('clients:detail', id=pk)
    
    else:
        form = AddCommentForm()

    return render(request, 'client/client_detail.html',{
        'client': client,
        'form': form,
        'fileform': AddFileForm(),
    })

@login_required
def add_client(request):
    team = request.user.userprofile.active_team
    if request.method == "POST":
        form = AddClientForm(request.POST)
        if form.is_valid():
            client = form.save(commit=False)
            client.created_by = request.user
            client.team = team
            client.save()
            messages.success(request, 'The client was created.')
            return redirect('clients:list')
    else:
        form = AddClientForm()
    return render(request, 'client/add_client.html', {
        'form': form,
        'team': team
    })

@login_required
def client_delete(request, pk):
    client = get_object_or_404(Client, created_by=request.user, pk=pk)
    client.delete()
    messages.success(request, 'The client was deleted.')
    return redirect('clients:list')

@login_required
def client_edit(request, pk):
    client=get_object_or_404(Client, created_by=request.user, pk=pk)
    if request.method == "POST":
        form = AddClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, 'The client was saved.')
            return redirect('clients:list')
    else:
        form = AddClientForm(instance=client)

    return render(request, 'client/client_edit.html', {
        'form': form,

    })