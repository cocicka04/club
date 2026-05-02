from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import BookingForm
from .models import Booking
from places.models import Place
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
import qrcode
from io import BytesIO
import base64
from django.core.paginator import Paginator
from decimal import Decimal


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
            booking = form.save(commit=False)
            start = booking.start_time
            end = booking.end_time
            duration = (end - start).total_seconds() / 3600

            if duration > 24:
                form.add_error('end_time', 'Нельзя бронировать более чем на 24 часа')

            # длительность в часах
            duration = (end - start).total_seconds() / 3600

            price_per_hour = booking.place.tariff.price_per_hour

            total_price = Decimal("0")
            original_price = Decimal("0")

            current_time = start

            while current_time < end:
                next_hour = current_time + timedelta(hours=1)

                hour_price = price_per_hour
                original_price += hour_price

                # проверка ночного времени
                if current_time.hour >= 22 or current_time.hour < 8:
                    hour_price *= Decimal("0.95")  # -5%

                total_price += hour_price
                current_time = next_hour


            # скидка за длительность
            discount_percent = Decimal("0")

            if duration >= 3:
                discount_percent += Decimal("10")

            if discount_percent > 0:
                total_price = total_price * (Decimal("1") - discount_percent / Decimal("100"))


            # сохраняем
            booking.total_price = total_price
            booking.original_price = original_price
            booking.discount_percent = discount_percent
            if place:
                booking.place = place
            else:
                booking.place = form.cleaned_data.get('place')

            conflicts = Booking.objects.filter(
                place=booking.place,
                status=Booking.STATUS_ACTIVE,
                start_time__lt=booking.end_time,
                end_time__gt=booking.start_time
            )

            if conflicts.exists():
                form.add_error('start_time', "На это время место уже занято")
            else:
                booking.user = request.user
                booking.save()  # ← ВАЖНО: один save
                return redirect('booking:success', booking.id)
    else:
        initial = {}
        if place:
            initial['place'] = place
            initial['start_time'] = (
                timezone.now() + timedelta(minutes=10)
            ).strftime("%Y-%m-%dT%H:%M")

        form = BookingForm(initial=initial)

    places = Place.objects.all()
    existing_booking = None
    free_from = None
    free_to = None

    MIN_GAP = timedelta(hours=1)

    if place:
        now = timezone.now()

        bookings = Booking.objects.filter(
            place=place,
            status=Booking.STATUS_ACTIVE,
            end_time__gt=now
        ).order_by('start_time')

        if not bookings.exists():
            free_from = now
            free_to = now + timedelta(hours=24)

        else:
            first_booking = bookings.first()
            if first_booking.start_time > now:
                gap = first_booking.start_time - now

                if gap >= MIN_GAP:
                    free_from = now
                    free_to = first_booking.start_time
                else:
                    chain_end = first_booking.end_time

                    for booking in bookings[1:]:
                        if booking.start_time <= chain_end:
                            chain_end = max(chain_end, booking.end_time)
                        else:
                            gap = booking.start_time - chain_end

                            if gap >= MIN_GAP:
                                free_from = chain_end
                                free_to = booking.start_time
                                break
                            else:
                                chain_end = booking.end_time

                    if not free_from:
                        existing_booking = chain_end
            else:
                chain_end = first_booking.end_time

                for booking in bookings[1:]:
                    if booking.start_time <= chain_end:
                        chain_end = max(chain_end, booking.end_time)
                    else:
                        gap = booking.start_time - chain_end

                        if gap >= MIN_GAP:
                            free_from = chain_end
                            free_to = booking.start_time
                            break
                        else:
                            chain_end = booking.end_time

                if not free_from:
                    existing_booking = chain_end
                else:
                    existing_booking = chain_end

    return render(
        request,
        'booking/create_booking.html',
        {
            'form': form,
            'place': place,
            'places': places,
            'existing_booking': existing_booking,
            'free_from': free_from,
            'free_to': free_to
        }
    )


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
            new_booking = form.save(commit=False)
            new_booking.user = request.user
            new_booking.place = b.place

            conflicts = Booking.objects.filter(
                place=new_booking.place,
                status=Booking.STATUS_ACTIVE,
                start_time__lt=new_booking.end_time,
                end_time__gt=new_booking.start_time
            )

            if conflicts.exists():
                form.add_error(None, "В выбранный интервал место уже занято.")
            else:
                new_booking.save()
                return redirect('users:profile')
    else:
        form = BookingForm(initial={
            'place': b.place.id,
            'start_time': b.end_time.strftime("%Y-%m-%dT%H:%M"),
            'hours': 1
        })

    return render(
        request,
        'booking/create_booking.html',
        {'form': form, 'place': b.place}
    )

@login_required
def booking_success(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)

    qr_data = f"Booking #{booking.id} | Place {booking.place.number} | Code {booking.code}"

    qr = qrcode.make(qr_data)

    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    return render(request, 'booking/success.html', {
        'booking': booking,
        'qr_code': qr_base64
    })