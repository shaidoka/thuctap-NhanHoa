from .models import Team

def active_team(request):
    if request.user.is_authenticated():
        active_team = Team.objects.filter(created_by=request.user)[0]
    else:
        active_team = None
    return {'active_team': active_team}