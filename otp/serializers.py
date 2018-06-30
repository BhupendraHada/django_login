from rest_framework import serializers
from .helpers import send_otp
from .models import OTP

BINDING_KEYS = {
    'otp_code_created': 'otp.code.created',
    'otp_code_forgot': 'otp.code.forgot',
}

class OTPBaseSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(default=True)

    class Meta:
        model = OTP
        fields = ('id', 'contact_number', 'is_active')


class OTPCreateSerializer(OTPBaseSerializer):

    def create(self, validated_data):
        otp = send_otp(
            BINDING_KEYS['otp_code_created'], validated_data['contact_number'])
        return otp


class OTPVerifySerializer(serializers.Serializer):
    contact_number = serializers.CharField(required=True)
    key = serializers.CharField(required=True)


class OTPForgotSerializer(OTPBaseSerializer):

    def create(self, validated_data):
        # SMS OTP Subscriber
        return send_otp(
            BINDING_KEYS['otp_code_forgot'], validated_data['contact_number'])
