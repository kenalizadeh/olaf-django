from django.conf import settings
from django.utils.crypto import get_random_string as random_password
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from user.models import User, Device, UserProfile
from user.utils import jwt_encode
from user.serializers.serializers import *
from authy.api import AuthyApiClient
from olaf.tasks import send_sms_to
from core.paginators import DefaultPagination
from user.forms import MerchantLoginForm

from django.contrib.auth import authenticate
from django.contrib.gis import geos


authy_api = AuthyApiClient(settings.ACCOUNT_SECURITY_API_KEY)


class TFACodeValidation(APIView):

    permission_classes = (AllowAny,)

    model_class = User
    serializer_class = UserSerializer

    def post(self, request):

        user_data = request.data

        phone_number = user_data.get('phone_number')
        verification_token = user_data.get('verification_token')
        user_device_id = user_data.get('device')

        verification = authy_api.phones.verification_check(
            phone_number,
            '994',
            verification_token
        )

        if verification.ok():
            try:
                user = self.model_class.objects.get(phone_number=phone_number)

                if user_device_id:
                    device, created = Device.objects.update_or_create(
                        device_id=user_device_id,
                        defaults={
                            'user': user
                        }
                    )

                serializer = self.serializer_class(user, many=False)

                token = jwt_encode(user)
                return Response({'token': token, 'user': serializer.data}, status=status.HTTP_200_OK)

            except self.model_class.DoesNotExist:

                user_data['password'] = random_password() + random_password()

                serializer = self.serializer_class(data=user_data)
                serializer.is_valid(raise_exception=True)
                user_instance = serializer.save()

                if user_device_id:
                    device, created = Device.objects.update_or_create(
                        device_id=user_device_id,
                        defaults={
                            'user': user_instance
                        }
                    )

                token = jwt_encode(user_instance)
                return Response({'token': token, 'user': serializer.data}, status=status.HTTP_201_CREATED)
        else:
            res = {'Bad Request': 'Verification token is invalid'}
            return Response(res, status=status.HTTP_400_BAD_REQUEST)


class PhoneNumberVerificationRequest(APIView):

    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):

        phone_number = request.data.get('phone_number')

        if not phone_number:
            return Response({'Error': 'phone_number is required'}, status=status.HTTP_400_BAD_REQUEST)

        send_sms_to.delay(phone_number)
        return Response(status=status.HTTP_200_OK)


class MerchantLoginView(APIView):

    permission_classes = (AllowAny,)
    model_class = User

    def post(self, request, *args, **kwargs):

        form = MerchantLoginForm(request.data)

        if not form.is_valid():
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

        phone_number = form.cleaned_data['phone_number']
        password = form.cleaned_data['password']

        user = authenticate(phone_number=phone_number, password=password)

        if user is not None and user.is_business:

            token = jwt_encode(user)
            return Response({'token': token}, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


class AuthenticateUser(APIView):

    permission_classes = (AllowAny,)

    model_class = User

    def post(self, request):
        try:
            phone_number = request.data.get('phone_number')

            try:
                user = self.model_class.objects.get(phone_number=phone_number)

                token = jwt_encode(user)
                return Response({'token': token}, status=status.HTTP_200_OK)

            except self.model_class.DoesNotExist:
                res = {
                    'error': 'can not authenticate with the given credentials or the account has been deactivated'}
                return Response(res, status=status.HTTP_403_FORBIDDEN)
        except KeyError:
            res = {'error': 'please provide phone number'}
            return Response(res)


class UserProfileView(APIView):

    def get(self, request):

        serializer = UserProfileSerializer(request.user.profile, many=False, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):

        serializer = UserProfileUpdateSerializer(request.user.profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        profile = serializer.save()

        serializer = UserProfileSerializer(profile, many=False, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserActivityUpdateView(APIView):

    def put(self, request):

        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')

        if not latitude or not longitude:
            res = {'Error': 'latitude and longitude must be provided'}
            return Response(res, status=status.HTTP_400_BAD_REQUEST)

        gis_location = geos.Point(longitude, latitude)

        activity, created = UserActivity.objects.update_or_create(
            user=request.user,
            defaults={
                'gis_location': gis_location,
            }
        )

        serializer = UserActivitySerializer(activity, many=False)

        return Response(serializer.data, status=status.HTTP_200_OK)


class FootNoteView(APIView):

    model_class = FootNote
    serializer_class = FootNoteDetailSerializer

    def get(self, request, footnote_id):

        try:
            footnote = self.model_class.objects.get(user=request.user, pk=footnote_id)
            serializer = self.serializer_class(footnote)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except self.model_class.DoesNotExist:

            return Response({'Error': 'Footnote does not exist'}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, footnote_id):

        try:
            footnote = self.model_class.objects.get(user=request.user, pk=footnote_id)
            footnote.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)
        except self.model_class.DoesNotExist:

            return Response({'Error': 'Footnote does not exist'}, status=status.HTTP_400_BAD_REQUEST)


class FootNoteCreateView(APIView):

    serializer_class = FootNoteCreateSerializer

    def post(self, request):

        footnote_data = request.data
        footnote_data['user'] = request.user.pk

        serializer = self.serializer_class(data=footnote_data)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(status=status.HTTP_201_CREATED)


class FootNoteListView(ListAPIView):

    model_class = FootNote
    serializer_class = FootNoteDetailSerializer
    pagination_class = DefaultPagination

    def get(self, request, *args, **kwargs):

        queryset = self.model_class.objects.filter(user=self.request.user)
        serializer = self.serializer_class(queryset, many=True, context={'request': self.request})

        page = self.paginate_queryset(serializer.data)

        return self.get_paginated_response(page)


class FootNoteCreateTestView(APIView):

    def post(self, request):

        data = request.data

        footnote_pk = data.get('id')
        
        if footnote_pk:
            
            try:
                footnote = FootNote.objects.get(pk=footnote_pk)

            except FootNote.DoesNotExist:
                return Response({'Error': 'Footnote does not exist'}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = FootNoteDetailSerializer(footnote)

            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            
            data['user'] = request.user.pk

            serializer = FootNoteCreateSerializer(data=data)
            serializer.is_valid(raise_exception=True)

            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
