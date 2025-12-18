from django.utils import timezone
from .models import Booking

def finish_expired_bookings(user=None):
    qs = Booking.objects.filter(
        status=Booking.STATUS_ACTIVE,
        end_time__lte=timezone.now()
    )
    if user:
        qs = qs.filter(user=user)

    qs.update(status=Booking.STATUS_FINISHED)
