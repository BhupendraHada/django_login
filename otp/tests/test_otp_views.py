from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APIClient

from otp.models import OTP
from otp.views import verify_otp


class OTPViewsTests(APITestCase):
    authenticated_client = APIClient()

    def setUp(self):
        self.user = get_user_model()(
            username='test12345',
            email='test123@test.com',
            password='12345',
            first_name='XX',
            contact_number='1234567890'
        )
        self.user.save()
        token = Token.objects.get(user__username=self.user.username)
        self.authenticated_client.credentials(
            HTTP_AUTHORIZATION='Token {}'.format(token.key))

        self.otp_create_url = reverse('otp:create')
        self.otp_detail_url = reverse('otp:detail')
        self.otp_forgot_url = reverse('otp:forgot')

        self.data = {
            'contact_number': '1234567890'
        }

    def test_create_otp_url(self):
        """
        OTP url
        """

        self.assertEqual(self.otp_create_url, '/api/v1/otp/create/')

    def test_create_otp_key(self):
        """
        Create OTP
        """

        response = self.authenticated_client.post(
            self.otp_create_url, self.data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(response.data['contact_number'], '1234567890')
        self.assertFalse("key" in response.data)

        # is_active should be True

        otp = OTP.objects.filter(
            contact_number=response.data['contact_number']).order_by('-id')[0]
        self.assertTrue(otp.is_active)

    def test_create_otp_without_mobile_no(self):
        """
        400 Error. Try to create OTP Without contact_number field.
        """
        data = {}

        response = self.authenticated_client.post(
            self.otp_create_url, data, format='json')
        self.assertEqual(response.status_code, 400)

        self.assertEqual(response.data.get("contact_number"),
                         ["This field is required."])

    # Test case is invalid
    def test_otp_detail_view(self):
        response = self.authenticated_client.post(
            self.otp_create_url, self.data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        otp = OTP.objects.get(
            contact_number=response.data.get('contact_number'))
        # is_verfied should be False
        # self.assertEqual(user.is_verified, False)
        data = {
            'key': otp.key,
            'contact_number': response.data.get('contact_number')
        }

        get_response = self.authenticated_client.post(
            self.otp_detail_url, data, format='json')
        self.assertEqual(get_response.data.get('is_exists'), True)

        # Test Again. Now OTP disabled. And is_exists should be False.
        data = {
            'key': otp.key,
            'contact_number': response.data.get('contact_number')
        }

        response = self.authenticated_client.post(
            self.otp_detail_url, data, format='json')
        self.assertEqual(response.data.get('is_exists'), False)

    def test_invalid_serailizer(self):
        # in_valid serailizer
        data = {
        }

        response = self.authenticated_client.post(
            self.otp_detail_url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data.get("contact_number"),
                         ["This field is required."])
        self.assertEqual(response.data.get("key"),
                         ["This field is required."])

    def test_invalid_otp(self):
        """
        Test Invalid OTP Code.
        """

        data = {
            'contact_number': '1234',
            'key': '34'
        }
        response = self.authenticated_client.post(
            self.otp_detail_url, data, format='json')

        self.assertEqual(response.data.get('is_exists'), False)

    def test_create_otp_and_disable_previous_codes(self):
        """
        Create OTP code & disabled previous generated code tests
        """

        self.authenticated_client.post(
            self.otp_create_url, self.data, format='json')

        self.authenticated_client.post(
            self.otp_create_url, self.data, format='json')

        # self.authenticated_client.post(
        #     self.otp_create_url, self.data, format='json')
        #
        # self.authenticated_client.post(
        #     self.otp_create_url, self.data, format='json')

        otp_5 = self.authenticated_client.post(
            self.otp_create_url, self.data, format='json')

        otp_codes = OTP.objects.filter(
            is_active=True, contact_number=otp_5.data['contact_number'])
        # Only 1 Active code should be active at a time.
        self.assertEqual(otp_codes.count(), 1)

        # is_active should be True
        otp = OTP.objects.filter(
            contact_number=otp_5.data['contact_number']).order_by('-id').first()
        self.assertTrue(otp.is_active)

    def test_verify_otp(self):
        # test verify_otp function
        response = self.authenticated_client.post(
            self.otp_create_url, self.data, format='json')
        # self.assertEqual(response.data.get, 1)
        otp = OTP.objects.get(
            contact_number=response.data.get('contact_number'))
        verified = verify_otp(
            contact_number=response.data.get('contact_number'),
            otp_key=otp.key
        )
        self.assertEqual(verified, True)
        verified = verify_otp(
            contact_number=response.data.get('contact_number'),
            otp_key='12234'
        )
        self.assertEqual(verified, False)

    def test_otp_forgot_key(self):
        """
        Forgot OTP
        """

        response = self.authenticated_client.post(
            self.otp_forgot_url, self.data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(response.data['contact_number'], '1234567890')
        self.assertFalse("key" in response.data)
