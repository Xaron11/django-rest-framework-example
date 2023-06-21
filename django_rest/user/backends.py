from django.contrib.auth.backends import BaseBackend
from .models import User


class AuthBackend(BaseBackend):

    def authenticate(self, request, password=None, key='username', **kwargs):
        login = kwargs.get(key, None)

        if login is None or password is None:
            return

        try:
            user = User.objects.get(**{key: login})
        except User.DoesNotExist:
            User().set_password(password)
        else:
            if user.check_password(password) and user.is_active:
                return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
