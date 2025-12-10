# places/views.py
from django.shortcuts import render, get_object_or_404
from .models import Place

def place_list(request):
    places = Place.objects.filter(is_active=True)
    return render(request, 'places/place_list.html', {'places': places})

def place_detail(request, pk):
    place = get_object_or_404(Place, pk=pk)
    return render(request, 'places/place_detail.html', {'place': place})
