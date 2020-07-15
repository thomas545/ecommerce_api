from rest_framework_jwt.serializers import VerifyJSONWebTokenSerializer


class JwtTokenAuthMiddleware:
    """
    JWT token authorization middleware for Django Channels 2
    """

    def __init__(self, inner):
        self.inner = inner

    def __call__(self, scope):
        try:
            token_header = dict(scope["headers"])[b"authorization"].decode().split()
            data = {"token": token_header[1]}
            valid_data = VerifyJSONWebTokenSerializer().validate(data)
            user = valid_data["user"]
            scope["user"] = user
        except:
            pass
        return self.inner(scope)
