from django.shortcuts import render
from .models import Tariff

def tariffs_list(request):
    tariffs = Tariff.objects.select_related('category').all()
    return render(request, 'tariffs/list.html', {'tariffs': tariffs})
