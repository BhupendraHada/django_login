from django.test import TestCase

from otp.models import OTP


class OTPTests(TestCase):
    def setUp(self):
        self.otp = OTP(
            contact_number='1234'
        )
        self.otp.save()

    def test_mobile_no(self):
        self.assertEqual(
            self.otp.contact_number, '1234')

    def test_otp_unicode(self):

        self.assertEqual(
            self.otp.__unicode__(), self.otp.contact_number)
