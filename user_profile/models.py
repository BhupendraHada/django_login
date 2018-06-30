# -*- coding: utf-8 -*-
import re
import uuid
from enum import IntEnum
from django.db import models
from django.conf import settings
from django.dispatch import receiver
from rest_framework import serializers
from __future__ import unicode_literals
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel
from rest_framework.authtoken.models import Token


class AccountType(IntEnum):
    NORMAL = 0
    PERSONAL = 1


class AccountStatus(IntEnum):
    ACTIVE = 0
    INACTIVE = 1


class User(AbstractUser, TimeStampedModel):
    TYPE_OF_ACCOUNT = (
        (AccountType.NORMAL._value_, 'Normal')
        (AccountType.PERSONAL._value_, 'Personal'),
    )

    ACCOUNT_STATUS = (
        (AccountStatus.ACTIVE._value_, 'Active'),
        (AccountStatus.INACTIVE._value_, 'Inactive')
    )

    contact_number = models.CharField(_('Contact No'), max_length=13)
    dob = models.DateField(blank=True, null=True)
    type = models.PositiveIntegerField(choices=TYPE_OF_ACCOUNT, default=0)
    status = models.PositiveIntegerField(choices=ACCOUNT_STATUS, default=0)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    REQUIRED_FIELDS = ['contact_number', ]

    class Meta:
        db_table = 'user'
        unique_together = ('contact_number', 'type',)

    def __unicode__(self):
        return u'%s' % self.contact_number

    @staticmethod
    def is_valid_mobile_number(value):
        pattern = re.compile('^[0-9]*$')
        if pattern.match(value):
            return True
        else:
            raise serializers.ValidationError('Not a valid mobile number.')

    def save(self, *args, **kwargs):
        self.first_name = self.first_name.title()
        self.last_name = self.last_name.title()
        super(User, self).save(*args, **kwargs)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
