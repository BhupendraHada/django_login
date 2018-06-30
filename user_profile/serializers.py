
import re
import logging
from django.conf import settings
from rest_framework import serializers
from django.db.transaction import atomic
from rest_framework.validators import UniqueValidator

from user_profile.models import User

logger = logging.getLogger(__name__)


def is_valid_mobile_number(value):
    pattern = re.compile('^[0-9]*$')
    if pattern.match(value):
        return True
    else:
        raise serializers.ValidationError('Not a valid mobile number.')


class BaseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('password',)


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())], required=False, allow_blank=True)

    contact_number = serializers.CharField(max_length=13, min_length=10,
                                           validators=[UniqueValidator(queryset=User.objects.all()),
                                                       is_valid_mobile_number])

    username = serializers.CharField(required=False,
                                     validators=[UniqueValidator(queryset=User.objects.all()), ])

    password = serializers.CharField(required=False, write_only=True)

    image_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'uuid', 'email', 'password', 'first_name', 'last_name', 'contact_number', 'dob', 'username',
            'image_url', 'created', 'modified', 'is_active', 'groups', 'is_verified')
        extra_kwargs = {'is_active': {'write_only': True,
                                      'default': True},
                        'image_url': {'required': False,
                                      'read_only': True},
                        'created': {'required': False},
                        'modified': {'required': False},
                        'groups': {'required': False,
                                   'read_only': True},
                        'is_verified': {'required': False,
                                        'read_only': True}}

    def get_image_url(self, obj):
        return "{}user_images/{}".format(settings.CDN_BASE_URL, obj.image_url)

    @atomic
    def create(self, validated_data):
        validated_data["is_verified"] = True
        user_obj = User.objects.create(validated_data)
        return user_obj
