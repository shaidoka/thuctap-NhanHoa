from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from leads.models import Lead
from client.models import Client
from team.models import Team

# Create your views here.
@login_required
def dashboard(request):
    team = request.user.userprofile.active_team
    leads = Lead.objects.filter(team=team, converted_to_client=False).order_by('-created_at')[0:5]
    clients = Client.objects.filter(team=team).order_by('-created_at')[0:5]
    
    return render(request, 'dashboard/dashboard.html', {
        'leads': leads,
        'clients': clients,
    })