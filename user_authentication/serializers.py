from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from rest_framework import exceptions, serializers
from social.apps.django_app.utils import psa
from social.apps.django_app.utils import load_strategy, load_backend
from django.core.exceptions import ObjectDoesNotExist
from user_profile.models import User
from user_profile.serializers import BaseUserSerializer
from otp.views import verify_otp
from user_authentication.views import AuthBackend


class SocialAuthSerializer(serializers.Serializer):
    accessToken = serializers.CharField()

    class Meta:
        model = User
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        access_token = attrs.get('accessToken')
        backend = self.context['backend']

        if access_token:
            user = register_by_access_token(self.context['request'], AuthBackend.get_backend_text(backend))

            if user:
                if not user.is_active:
                    msg = _('User account is disabled.')
                    raise exceptions.ValidationError(msg)
            else:
                msg = _('Unable to log in with provided credentials.')
                raise exceptions.ValidationError(msg)
        else:
            msg = _('Must include "accessToken" and "backend".')
            raise exceptions.ValidationError(msg)

        data = dict()
        data['user'] = BaseUserSerializer(user).data
        data['token'] = user.auth_token.key

        return data


class AuthTokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    account_type = serializers.CharField(required=False)

    class Meta:
        extra_kwargs = {'password': {'write_only': True}}

    def authenticate(self, username, password, account_type):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.custom_get_by_natural_key(username, account_type)
            if user.check_password(password):
                return user
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a non-existing user (#20760).
            UserModel().set_password(password)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        account_type = attrs.get('account_type', 0)

        if username and password:
            user = self.authenticate(username=username, password=password, account_type=account_type)

            if user:
                if not user.is_active:
                    msg = _('User account is disabled.')
                    raise exceptions.ValidationError(msg)
            else:
                msg = _('Unable to log in with provided credentials.')
                raise exceptions.ValidationError(msg)
        else:
            msg = _('Must include "username" and "password".')
            raise exceptions.ValidationError(msg)

        data = dict()
        user_data = BaseUserSerializer(user).data
        data['account'] = user_data
        data['user'] = user_data
        data['token'] = user.auth_token.key

        return data


class AuthOTPSerializer(serializers.Serializer):
    contact_number = serializers.CharField()
    otp = serializers.CharField()

    class Meta:
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        contact_number = attrs.get('contact_number')
        otp = attrs.get('otp')
        account_type = attrs.get('account_type', 0)
        try:
            user = User.objects.get(contact_number=contact_number, type=account_type)
            if verify_otp(contact_number=contact_number, otp_key=otp):
                if not user.is_active:
                    msg = _('User account is disabled.')
                    raise exceptions.ValidationError(msg)
                user.is_verified = True
                user.save()
            else:
                raise serializers.ValidationError({"otp": "Wrong OTP"})

            data = dict()

            # sending user information in account object along with user object since it's used in website as well.

            user_data = BaseUserSerializer(user).data
            data['account'] = user_data
            data['user'] = user_data
            data['token'] = user.auth_token.key
            return data
        except ObjectDoesNotExist:
            raise serializers.ValidationError({"user": "User does not exist"})


@psa()
def register_by_access_token(request, backend):
    uri = ''

    strategy = load_strategy(request)
    backend = load_backend(strategy, backend, uri)  # Split by spaces and get the array
    if request.data['accessToken'] is None:
        msg = 'No access token provided.'
        return msg
    else:
        access_token = request.data['accessToken']

    # Real authentication takes place here
    user = backend.do_auth(access_token)
    return user
