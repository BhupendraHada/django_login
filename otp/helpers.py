__author__ = 'bhupendra'

from .models import OTP
from .utils import call_publisher, get_random_key


def send_otp(routing_key, contact_number):
    updated_values = {}
    updated_values.update({'key': get_random_key()})
    updated_values.update({'is_active': True})
    otp, created = OTP.objects.update_or_create(
        contact_number=contact_number, defaults=updated_values)
    # SMS OTP Subscriber
    call_publisher(
        routing_key=routing_key,
        contact_number=otp.contact_number,
        key=otp.key)
    return otp
