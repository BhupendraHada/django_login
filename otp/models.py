from django.db import models

from model_utils.models import TimeStampedModel

from .utils import get_random_key


class OTP(TimeStampedModel):
    contact_number = models.CharField(
        max_length=16,
        help_text="The mobile number to deliver tokens to."
    )

    key = models.CharField(
        max_length=4,
        # validators=[key_validator],
        default=get_random_key
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('key', 'contact_number')

    def __unicode__(self):
        return self.contact_number
