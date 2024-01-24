from django.contrib import admin
from .models import Lead, Comment, LeadFile

# Register your models here.
admin.site.register(Lead)
admin.site.register(Comment)
admin.site.register(LeadFile)