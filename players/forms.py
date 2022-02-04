from django import forms
from django.forms import ModelForm
from .models import RaidEvent

class Eventform(ModelForm):
    class Meta:
        model = RaidEvent
        fields = ('name', 'date')
        labels = {
            'name': '',
            'date': '',
        }

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Event name'}),
            'date': forms.SelectDateWidget(attrs={'class': 'form-control', 'placeholder':'Date'})
        }