from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from .models import Place
from .forms import PlaceForm
from booking.models import Booking
from django.utils import timezone
from tariffs.models import Tariff
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.db.models import Exists, OuterRef, Prefetch
from datetime import timedelta


def place_list(request):
    now = timezone.now()
    
    places = Place.objects.select_related('tariff', 'category').all()

    # --- фильтры ---
    search = request.GET.get('search')
    if search:
        places = places.filter(title__icontains=search)

    tariff = request.GET.get('tariff')
    if tariff:
        places = places.filter(tariff_id=tariff)

    min_price = request.GET.get('min_price')
    if min_price:
        places = places.filter(tariff__price_per_hour__gte=min_price)

    max_price = request.GET.get('max_price')
    if max_price:
        places = places.filter(tariff__price_per_hour__lte=max_price)

    # ✅ Активная сессия (ИМЕННО сейчас идет)
    active_bookings = Booking.objects.filter(
        place=OuterRef('pk'),
        status=Booking.STATUS_ACTIVE,
        start_time__lte=now,
        end_time__gt=now
    )

    # 🎯 Prefetch для получения активного бронирования (чтобы был доступ к end_time)
    places = places.prefetch_related(
        Prefetch(
            'booking_set',
            queryset=Booking.objects.filter(
                status=Booking.STATUS_ACTIVE,
                start_time__lte=now,
                end_time__gt=now
            ),
            to_attr='active_bookings_list'
        )
    ).annotate(
        is_busy=Exists(active_bookings)
    )

    # ✅ Добавляем active_booking как свойство для каждого места
    for place in places:
        place.active_booking = place.active_bookings_list[0] if place.active_bookings_list else None

    # пагинация
    paginator = Paginator(places, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'places/place_list.html', {
        'places': page_obj,
        'tariffs': Tariff.objects.all()
    })


def place_detail(request, pk):
    place = get_object_or_404(Place, pk=pk)
    now = timezone.now()
    MIN_GAP = timedelta(hours=1)

    bookings = Booking.objects.filter(
        place=place,
        status=Booking.STATUS_ACTIVE,
        end_time__gt=now
    ).order_by('start_time')

    final_end_time = None
    free_from = None
    free_to = None

    if bookings.exists():
        chain_end = now

        for booking in bookings:
            # если бронь перекрывает текущую цепочку
            if booking.start_time <= chain_end:
                chain_end = max(chain_end, booking.end_time)
            else:
                # нашли разрыв
                gap = booking.start_time - chain_end

                if gap >= MIN_GAP:
                    free_from = chain_end
                    free_to = booking.start_time
                    final_end_time = None
                    break
                else:
                    # маленький разрыв → продолжаем цепочку
                    chain_end = booking.end_time

        if not free_from:
            final_end_time = chain_end

    active_booking = Booking.objects.filter(
        place=place,
        status=Booking.STATUS_ACTIVE,
        start_time__lte=now,
        end_time__gt=now
    ).first()

    return render(request, 'places/place_detail.html', {
        'place': place,
        'active_booking': active_booking,
        'final_end_time': final_end_time,
        'free_from': free_from,
        'free_to': free_to
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


def place_search_ajax(request):
    now = timezone.now()
    
    places = Place.objects.select_related('tariff', 'category').all()

    # --- фильтры ---
    search = request.GET.get('search')
    if search:
        places = places.filter(title__icontains=search)

    tariff = request.GET.get('tariff')
    if tariff:
        places = places.filter(tariff_id=tariff)

    min_price = request.GET.get('min_price')
    if min_price:
        places = places.filter(tariff__price_per_hour__gte=min_price)

    max_price = request.GET.get('max_price')
    if max_price:
        places = places.filter(tariff__price_per_hour__lte=max_price)

    # ✅ Та же логика для AJAX
    active_bookings = Booking.objects.filter(
        place=OuterRef('pk'),
        status=Booking.STATUS_ACTIVE,
        start_time__lte=now,
        end_time__gt=now
    )

    places = places.prefetch_related(
        Prefetch(
            'booking_set',
            queryset=Booking.objects.filter(
                status=Booking.STATUS_ACTIVE,
                start_time__lte=now,
                end_time__gt=now
            ),
            to_attr='active_bookings_list'
        )
    ).annotate(
        is_busy=Exists(active_bookings)
    )

    # ✅ Добавляем active_booking для AJAX-результатов
    for place in places:
        place.active_booking = place.active_bookings_list[0] if place.active_bookings_list else None

    html = render_to_string('places/place_cards.html', {
        'places': places
    })

    return HttpResponse(html)