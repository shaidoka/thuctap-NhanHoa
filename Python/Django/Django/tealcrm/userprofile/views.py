from django.shortcuts import render, redirect
from .models import Userprofile
from django.contrib.auth.decorators import login_required
from .forms import SignupForm
from team.models import Team

# Create your views here.
def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            team = Team.objects.create(name='The team name', created_by=user)
            team.members.add(user)
            team.save()
            Userprofile.objects.create(user=user, active_team=team)
            return redirect('/log-in/')
    else:
        form = SignupForm()
    return render(request, 'userprofile/signup.html', {
        'form': form
    })

@login_required
def myaccount(request):
    team = request.user.userprofile.active_team

    return render(request, 'userprofile/myaccount.html', {
        'team': team
    })