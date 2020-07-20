from django.contrib.auth.backends import AllowAllUsersModelBackend
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied

# User = get_user_model()


class EmailBackend(AllowAllUsersModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get("username")
        # if User.objects.get(profile__phone_number=username).sms.first().verified == False:
        #     raise PermissionDenied("you can't login by phone Number")
        try:
            if (
                username[0] == "+"
            ):  # and User.objects.get(profile__phone_number=username).sms.first().verified == True:
                user = User.objects.get(profile__phone_number=username)
            else:
                user = User.objects.get(email=username)
        except User.DoesNotExist:
            raise PermissionDenied("This User does't exist.")

        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
