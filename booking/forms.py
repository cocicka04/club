from django import forms
from .models import Booking
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

class BookingForm(forms.ModelForm):
    hours = forms.IntegerField(label="Часы", min_value=1, max_value=24, initial=1)
    start_time = forms.DateTimeField(
        label="Время начала",
        input_formats=['%Y-%m-%dT%H:%M'],
        widget=forms.DateTimeInput(attrs={
        'type': 'datetime-local'})
    )

    class Meta:
        model = Booking
        fields = ('place', 'start_time', 'hours')

    def clean_start_time(self):
        st = self.cleaned_data['start_time']
        if st < timezone.now():
            raise forms.ValidationError("Время начала не может быть в прошлом")
        return st

    def save(self, commit=True, user=None):
        booking = super().save(commit=False)

        hours = self.cleaned_data.get('hours') or 1
        booking.end_time = booking.start_time + timedelta(hours=hours)
        booking.hours = hours

        price_per_hour = booking.place.tariff.price_per_hour if booking.place and booking.place.tariff else Decimal('0')

        total = Decimal('0')

        current_time = booking.start_time

        for i in range(hours):
            hour_price = price_per_hour

            # 🔹 скидка за длительность (всегда ко всем часам)
            if hours >= 3:
                hour_price *= Decimal('0.9')  # -10%

            # 🔹 ночная скидка (ТОЛЬКО на конкретный час)
            if current_time.hour >= 22 or current_time.hour < 8:
                hour_price *= Decimal('0.95')  # -5%

            total += hour_price
            current_time += timedelta(hours=1)

        booking.total_price = total

        if user:
            booking.user = user

        if commit:
            booking.save()

        return booking

