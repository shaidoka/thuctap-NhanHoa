from django.db import models
from django.contrib.auth.models import User

from team.models import Team

# Create your models here.
class Userprofile(models.Model):
    user = models.OneToOneField(User, related_name='userprofile', on_delete=models.CASCADE)
    active_team = models.ForeignKey(Team, related_name='userprofiles', blank=True, null=True, on_delete=models.CASCADE)