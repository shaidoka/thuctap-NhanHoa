from django import forms
from .models import Review
from django.forms import ModelForm

'''
class ReviewForm(forms.Form):
    first_name = forms.CharField(label="First Name", max_length=100)
    last_name = forms.CharField(label="Last Name", max_length=100)
    email = forms.EmailField(label="Last Name", max_length=100)
    review = forms.CharField(label="Please write your review here", widget=forms.Textarea(attrs={'class':'myform','rows':'2','cols':'2'}))
    '''

class ReviewForm(ModelForm):
    class Meta:
        model = Review
        fields = "__all__" # pass in all model fields as form field
        labels = {
            'first_name':"YOUR FIRST NAME",
            'last_name':"Last Name",
            'stars':"Rating"
        }

        error_messages = {
            'stars': {
                'min_value':"Min value is 1",
                'max_value':"Max value is 5"
            }
        }