from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class Car(models.Model):
    brand = models.CharField(max_length=50)
    year = models.IntegerField()
    def __str__(self) -> str:
        return f"Car is {self.brand} {self.year}"
    
class Review(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    stars = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])