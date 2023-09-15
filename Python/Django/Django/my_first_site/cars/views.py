from django.shortcuts import render, redirect
from . import models
from django.urls import reverse
from .forms import ReviewForm

# Create your views here.
def list(request):
    all_cars = models.Car.objects.all()
    context = {'all_cars':all_cars}
    return render(request,'cars/list.html',context=context)

def add(request):
    if request.POST:
        brand = request.POST['brand']
        year = int(request.POST['year'])
        models.Car.objects.create(brand=brand, year=year)
        return redirect(reverse('cars:list'))
    else:
        return render(request,'cars/add.html')

def delete(request):
    if request.POST:
        pk = request.POST['pk']
        try:
            models.Car.objects.get(pk=pk).delete()
            return redirect(reverse("cars:list"))
        except:
            print("PK not found!")
            return redirect(reverse("cars:list"))
    else:
        return render(request,'cars/delete.html')

def reviews(request):
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse("cars:thanks"))
    else:
        form = ReviewForm()
    return render(request, "cars/reviews.html",context={"form":form})

def thanks(request):
    return render(request, "cars/thanks.html")

