from django.conf import settings
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class OTPAnonRateThrottle(AnonRateThrottle):
    rate = settings.OTP_RATE_THROTTLE


class OTPUserRateThrottle(UserRateThrottle):
    rate = settings.OTP_RATE_THROTTLE
