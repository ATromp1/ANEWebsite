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
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Event name'}),
            'date': forms.DateInput(attrs=dict(type='date'))
        }

class EditEventForm(ModelForm):
    class Meta:
        model = RaidEvent
        fields = ('name',)
        labels = {
            'name': '',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Change Event Name'}),
        }
