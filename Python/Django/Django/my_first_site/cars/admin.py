from django.contrib import admin
from cars.models import Car
from .models import Review
# Register your models here.

class CarAdmin(admin.ModelAdmin):
    fieldsets = [
        ("TIME INFORMATION", {"fields":["year"]}),
        ("CAR INFORMATION", {"fields":["brand"]})
    ]

admin.site.register(Car, CarAdmin)
admin.site.register(Review)