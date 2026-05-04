from django import forms
from .models import Tariff, Category

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
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3})
        }
