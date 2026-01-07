from django import forms
from .models import Place

class PlaceForm(forms.ModelForm):
    class Meta:
        model = Place
        fields = [
            'title', 'number',
            'category', 'tariff',
            'description',
            'cpu', 'gpu', 'ram',
            'monitor', 'keyboard', 'mouse', 'headset',
            'image'
        ]
