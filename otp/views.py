import logging

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics
from rest_framework import mixins
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from profiles.models import User
from .models import OTP
from .serializers import (
    OTPCreateSerializer, OTPForgotSerializer, OTPVerifySerializer)
from .throttling import OTPAnonRateThrottle, OTPUserRateThrottle

logger = logging.getLogger(__name__)


class OTPCreateView(mixins.CreateModelMixin, generics.GenericAPIView):
    queryset = OTP.objects.all()
    serializer_class = OTPCreateSerializer
    throttle_classes = (OTPAnonRateThrottle, OTPUserRateThrottle)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class OTPForgotCreateView(mixins.CreateModelMixin, generics.GenericAPIView):
    queryset = OTP.objects.all()
    serializer_class = OTPForgotSerializer
    throttle_classes = (OTPAnonRateThrottle, OTPUserRateThrottle)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class OTPDetail(APIView):
    """
    Validate OTP code against mobile number.
    """

    def post(self, request, format=None):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            contact_number = serializer.validated_data['contact_number']
            key = serializer.validated_data['key']
            try:
                otp = OTP.objects.get(
                        contact_number=contact_number,
                        key=key,
                        is_active=True
                )
                otp.is_active = False
                try:
                    user = User.objects.get(contact_number=contact_number, type=0)
                    user.is_verified = True
                    user.save()
                except User.DoesNotExist:
                    logger.debug("OTP User Not found contact_number {}".format(contact_number))
                otp.save()
                data = {'is_exists': True}
            except OTP.DoesNotExist:
                data = {'is_exists': False}
                logger.error("Does not exists " + str(contact_number))
            return Response(data, status=200)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def verify_otp(contact_number=None, otp_key=None):
    try:
        otp = OTP.objects.get(
                contact_number=contact_number, key=otp_key, is_active=True)
        otp.is_active = False
        otp.save()
        return True
    except ObjectDoesNotExist:
        return False
