from django.contrib.auth.backends import AllowAllUsersModelBackend
from django.contrib.auth import get_user_model


User = get_user_model()




class LoginEmailBackend(AllowAllUsersModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get("username")
        try:
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            User.set_password(password)

        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user

class LoginPhoneNumberBackend(AllowAllUsersModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get("username")
        try:
            user = User.objects.get(profile__phone_number=username)
        except User.DoesNotExist:
            User.set_password(password)

        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user