# -*- coding: utf-8 -*-
import os
import json
import logging
from enum import IntEnum
from django.contrib import auth
from rest_framework import status
from __future__ import unicode_literals
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.authentication import (
    BasicAuthentication, SessionAuthentication, TokenAuthentication)
from rest_framework.decorators import api_view
from rest_framework.parsers import FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from otp.views import verify_otp
from user_profile.models import User
from .factories import AuthenticationSerializerFactory
from django.http import HttpResponse
from django.shortcuts import render
from django.http.response import JsonResponse
import requests

logger = logging.getLogger(__name__)


class BackendType(IntEnum):
    AUTH = 1
    OTP = 2


class AuthBackend(object):
    @staticmethod
    def get_backend_text(backend):
        return {
            BackendType.AUTH: "auth",
            BackendType.OTP: "otp",
        }[int(backend)]


class LoginView(APIView):
    """
    Authenticates a user according to the authentication backend
    and return token in the response.
    """
    parser_classes = (FormParser, JSONParser)

    def post(self, request, backend, format=None):
        try:
            data = request.data
            if backend is not None:
                serializer = AuthenticationSerializerFactory.get_authentication_serializer(
                        backend, data, request)
                if serializer.is_valid():
                    return Response(serializer.validated_data, status=status.HTTP_200_OK)
                logger.error(str(serializer.errors))
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"backend": ["Authentication backend is required"]}, status=status.HTTP_400_BAD_REQUEST)
        except BaseException as e:
            logger.error(str(e.message))
            return Response(e.message, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['POST', ])
def forgot_password(request):
    response_dic = dict()
    response_dic['meta'] = {"success": False}
    response_dic['payload'] = dict()
    try:
        request_data = request.data.get('payload')
        user = User.objects.get(contact_number=request_data['contact_number'])
        if verify_otp(contact_number=user.contact_number, otp_key=request_data['otp']):
            user.set_password(request_data['password'])
            user.is_verified = True
            user.save()
            response_dic['meta']['success'] = True
            response_dic['payload']['message'] = "Password Successfully Reset"
        else:
            response_dic['meta']['success'] = False
            response_dic['payload']['message'] = "OTP is Not Valid"
        return Response(data=response_dic, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        response_dic['payload']['message'] = "User does not Exist"
        return Response(data=response_dic, status=status.HTTP_404_NOT_FOUND)
    except KeyError:
        response_dic['payload']['message'] = "KeyError"
        return Response(data=response_dic, status=status.HTTP_404_NOT_FOUND)


@csrf_exempt
@api_view(['POST', ])
def logout(request):
    auth.logout(request)
    response_data = {'message': 'Successfully Logged Out'}
    response = HttpResponse(json.dumps(response_data), content_type="application/json")
    response.set_cookie(key='token', value='')
    return response


class ConsoleLogin(APIView):
    authentication_classes = (
        BasicAuthentication, SessionAuthentication, TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        base_dir = os.path.dirname(os.path.dirname(__file__))
        with open("{0}{1}".format(base_dir, "/user_authentication/config/console_login.json")) as json_file:
            json_data = json.load(json_file)
        response_list = self.get_console_data(request, json_data)
        return Response(response_list, status=status.HTTP_200_OK)

    @staticmethod
    def get_console_data(request, json_data):
        response = list()
        for data in json_data:
            if 'submenu' in data:
                data['submenu'] = ConsoleLogin.get_console_data(request, data['submenu'])
            if 'applicable_groups' in data and request.user.groups.filter(id__in=data['applicable_groups']):
                response.append(data)
        return response


class SellerLogin(APIView):
    authentication_classes = (
        BasicAuthentication, SessionAuthentication, TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        base_dir = os.path.dirname(os.path.dirname(__file__))
        with open("{0}{1}".format(base_dir, "/user_authentication/config/seller_login.json")) as json_file:
            json_data = json.load(json_file)
        response_list = self.get_seller_data(request, json_data)
        return Response(response_list, status=status.HTTP_200_OK)

    @staticmethod
    def get_seller_data(request, json_data):
        response = list()
        for data in json_data:
            if 'submenu' in data:
                data['submenu'] = SellerLogin.get_seller_data(request, data['submenu'])
            if 'applicable_groups' in data and request.user.groups.filter(id__in=data['applicable_groups']):
                response.append(data)
        return response


class ChangePassword(APIView):
    authentication_classes = (
        BasicAuthentication, SessionAuthentication, TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = dict()
        response['message'] = "Something Went Wrong"
        try:
            password = request.data['password']
            user = request.user
            user.set_password(password)
            user.save()
            response['message'] = "Password Changed Successfully"
            return Response(response, status=status.HTTP_200_OK)
        except KeyError:
            response["message"] = "Please provide password in JSON"
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def get_secret(request):
    return render(request, "secret_reset.html", content_type="text/html")


@csrf_exempt
def reset_password_secret(request):
        GUPSHUP_SMS_URL = "http://enterprise.smsgupshup.com/GatewayAPI/rest?method=SendMessage&send_to={mobile_no}&msg={msg}&msg_type=TEXT&userid=2000145635&auth_scheme=plain&password=g8aaTK7So&v=1.1&format=text"
        data = json.loads(request.body)
        password = data['password']
        contact_number = data['contact_number']
        user = User.objects.get(contact_number=contact_number)
        user.set_password(password)
        user.save()

        msg = "Welcome, Here are your account details/login details: \nUsername: %s \nPassword: %s." % (contact_number, password)
        # msg = "Password reset your new password is %s" % (password)
        sms_url = GUPSHUP_SMS_URL.format(mobile_no=contact_number, msg=msg)
        try:
            resp = requests.get(sms_url)
        except Exception, e:
            pass
        return JsonResponse({}, status=200)


@csrf_exempt
def get_secret_details(request, contact_number):
    user = User.objects.get(contact_number=contact_number)
    result = {
        'first_name': user.first_name,
        'last_name': user.last_name
    }
    return JsonResponse(result, status=200)

