from .models import Jwt
from rest_framework import authentication
from rest_framework import exceptions
from . import jwt_utils
from django.conf import settings


class JwtAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        authorization = request.headers.get('Authorization', None)
        if not authorization:
            raise exceptions.AuthenticationFailed('No authorization token')
        token = authorization[7:]

        if not jwt_utils.verify_token(token, settings.SECRET_KEY):
            raise exceptions.AuthenticationFailed('Token is invalid or has expired')

        try:
            jwt = Jwt.objects.get(access=token)
        except Jwt.DoesNotExist:
            raise exceptions.AuthenticationFailed('Access token not found')

        return jwt.user, None

    def authenticate_header(self, request):
        return 'Bearer'
