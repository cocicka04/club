from django import forms
from .models import Tariff

class TariffForm(forms.ModelForm):
    class Meta:
        model = Tariff
        fields = [
            'category',
            'name',
            'price_per_hour',
            'description',
        ]

        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 4
            })
        }
