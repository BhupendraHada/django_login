from user_authentication.views import BackendType
from user_authentication.serializers import SocialAuthSerializer, AuthTokenSerializer, AuthOTPSerializer


class AuthenticationSerializerFactory(object):
    @staticmethod
    def get_authentication_serializer(backend, data, request):
        if int(backend) not in list(map(int, BackendType)):
            raise ValueError('Allowed backends types: ', list(map(int, BackendType)))
        return {
            BackendType.AUTH: AuthTokenSerializer(data=data, context={'request': request}),
            BackendType.OTP: AuthOTPSerializer(data=data, context={'request': request}),
            BackendType.FACEBOOK: SocialAuthSerializer(data=data, context={'request': request, 'backend': backend}),
            BackendType.GOOGLE: SocialAuthSerializer(data=data, context={'request': request, 'backend': backend}),
        }[int(backend)]
