
from django import forms
from .models import Person

class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ['name', 'age', 'date']  
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),  
        }
