from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from .models import Place
from .forms import PlaceForm
from booking.models import Booking
from django.utils import timezone

def place_list(request):
    places = Place.objects.all()

    for place in places:
        place.active_booking = Booking.objects.filter(
            place=place,
            status=Booking.STATUS_ACTIVE,
            end_time__gt=timezone.now()
        ).order_by('end_time').first()

    return render(request, 'places/place_list.html', {
        'places': places
    })



def place_detail(request, pk):
    place = get_object_or_404(Place, pk=pk)
    active_booking = Booking.objects.filter(
        place=place,
        status=Booking.STATUS_ACTIVE,
        end_time__gt=timezone.now()
    ).order_by('-end_time').first()

    return render(request, 'places/place_detail.html', {
        'place': place,
        'active_booking': active_booking
    })


@staff_member_required
def place_create(request):
    if not request.user.is_superuser:
        return redirect('places:list')

    form = PlaceForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('places:list')

    return render(request, 'places/place_form.html', {'form': form})



@staff_member_required
def place_edit(request, pk):
    place = get_object_or_404(Place, pk=pk)

    if request.method == 'POST':
        form = PlaceForm(request.POST, request.FILES, instance=place)
        if form.is_valid():
            form.save()
            return redirect('places:detail', pk=pk)
    else:
        form = PlaceForm(instance=place)

    return render(request, 'places/place_form.html', {
        'form': form,
        'place': place,
        'title': 'Редактирование места'
    })


@staff_member_required
def place_delete(request, pk):
    place = get_object_or_404(Place, pk=pk)
    place.delete()
    return redirect('places:list')
