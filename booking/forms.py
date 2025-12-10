# booking/forms.py
from django import forms
from .models import Booking
from django.utils import timezone
from datetime import timedelta

class BookingForm(forms.ModelForm):
    hours = forms.IntegerField(label="Часы", min_value=1, max_value=24, initial=1)
    start_time = forms.DateTimeField(
        label="Время начала",
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
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
        price_per_hour = booking.place.tariff.price_per_hour if booking.place and booking.place.tariff else 0
        booking.total_price = price_per_hour * hours
        if user:
            booking.user = user
        if commit:
            booking.save()
        return booking

