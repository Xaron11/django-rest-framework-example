from django.db import IntegrityError
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from . import jwt_utils
from .authentication import JwtAuthentication
from .models import Jwt
from .serializers import LoginSerializer, RegisterSerializer, RefreshSerializer
from user.models import User
from django.conf import settings
from django.contrib.auth import authenticate


class LoginView(APIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = authenticate(request, key='email', **serializer.validated_data)

            if not user:
                return Response({"error": "Invalid email or password"}, status.HTTP_404_NOT_FOUND)

            access, refresh = jwt_utils.get_tokens({'user_id': user.id}, settings.SECRET_KEY)

            Jwt.objects.filter(user=user).delete()
            Jwt.objects.create(user=user, access=access, refresh=refresh)

            return Response({'access': access, 'refresh': refresh}, status.HTTP_200_OK)

        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class RegisterView(APIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                User.objects.create_user(**serializer.validated_data)
            except IntegrityError:
                return Response({"error": "The user with that name or email already exists"}, status.HTTP_200_OK)

            return Response(status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class RefreshView(APIView):
    serializer_class = RefreshSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():

            if not jwt_utils.verify_token(serializer.validated_data['refresh'], settings.SECRET_KEY):
                return Response({"error": "Refresh token is invalid or has expired"}, status.HTTP_400_BAD_REQUEST)

            try:
                jwt = Jwt.objects.get(refresh=serializer.validated_data['refresh'])
            except Jwt.DoesNotExist:
                return Response({"error": "Refresh token not found"}, status.HTTP_400_BAD_REQUEST)

            access, refresh = jwt_utils.get_tokens({'user_id': jwt.id}, settings.SECRET_KEY)
            jwt.access = access
            jwt.refresh = refresh
            jwt.save(update_fields=['access', 'refresh'])
            return Response({'access': access, 'refresh': refresh}, status.HTTP_200_OK)

        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class SecureView(APIView):
    authentication_classes = [JwtAuthentication]

    def get(self, request):
        return Response({"data": "SECURE DATA"}, status.HTTP_200_OK)
