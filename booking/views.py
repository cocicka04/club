from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import BookingForm
from .models import Booking
from places.models import Place
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q

def is_place_available(place, start, end):
    return not Booking.objects.filter(
        place=place,
        status=Booking.STATUS_ACTIVE
    ).filter(
        Q(start_time__lt=end) &
        Q(end_time__gt=start)
    ).exists()


def place_list(request):
    places = Place.objects.all()
    return render(request, 'places/place_list.html', {'places': places})

@login_required
def create_booking(request, place_id=None):
    place = None
    if place_id:
        place = get_object_or_404(Place, id=place_id)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            # Если форма содержит выбор place, берем оттуда, иначе используем place из URL
            booking = form.save(commit=False, user=request.user)
            if not place:
                # У формы поле place должно быть валидно заполнено
                booking.place = form.cleaned_data.get('place')
            else:
                booking.place = place

            overlap = Booking.objects.filter(
                place=place,
                status=Booking.STATUS_ACTIVE,
                start_time__lt=end_time,
                end_time__gt=start_time
            ).exists()

            if overlap:
                form.add_error(None, "Это место уже занято на выбранное время")
                return render(request, 'booking/create.html', {'form': form})

            # проверка пересечений: запрещаем создание броней на один place с пересечением времени
            conflicts = Booking.objects.filter(place=booking.place, status='active').filter(
                start_time__lt=booking.end_time, end_time__gt=booking.start_time
            )
            if conflicts.exists():
                form.add_error(None, "В выбранный интервал место уже занято.")
            else:
                booking.user = request.user
                booking.save()
                return redirect('users:profile')
    else:
        initial = {}
        if place:
            initial['place'] = place
            # предложим старт сейчас + 10 минут (или оставить поле пустым)
            initial['start_time'] = (timezone.now() + timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M")
        form = BookingForm(initial=initial)
    # для рендера select с data-price: передадим все места (чтобы шаблон мог рендерить опции)
    places = Place.objects.all()
    return render(request, 'booking/create_booking.html', {'form': form, 'place': place, 'places': places})

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(
        Booking,
        id=booking_id,
        user=request.user,
        status=Booking.STATUS_ACTIVE
    )

    booking.status = Booking.STATUS_CANCELED
    booking.save()

    return redirect('users:profile')

@login_required
def extend_booking(request, booking_id):
    b = get_object_or_404(Booking, id=booking_id, user=request.user)
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            # Создадим новое бронирование с предзаполненным start_time = предыдущий end_time
            new_booking = form.save(commit=False)
            new_booking.user = request.user
            new_booking.place = b.place
            # Проверка конфликтов как выше
            conflicts = Booking.objects.filter(place=new_booking.place, status='active').filter(
                start_time__lt=new_booking.end_time, end_time__gt=new_booking.start_time
            )
            if conflicts.exists():
                form.add_error(None, "В выбранный интервал место уже занято.")
            else:
                new_booking.save()
                return redirect('users:profile')
    else:
        initial = {
            'place': b.place.id,
            'start_time': b.end_time.strftime("%Y-%m-%dT%H:%M"),
            'hours': 1
        }
        form = BookingForm(initial=initial)
    return render(request, 'booking/create_booking.html', {'form': form, 'place': b.place})
