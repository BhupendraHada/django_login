from django.contrib import admin
from django.db import models

from .models import OTP


class OTPAdmin(admin.ModelAdmin):
    search_fields = ('contact_number',)


admin.site.register(OTP, OTPAdmin)
