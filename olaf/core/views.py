from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response


class Healthz(APIView):

    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        return Response({'message': 'Healthz is ok. Everything is running perfectly.'}, status=status.HTTP_200_OK)


class PrivateHealthz(APIView):

    def get(self, request, *args, **kwargs):
        return Response({'message': 'Healthz is ok. Everything is running perfectly.'}, status=status.HTTP_200_OK)
