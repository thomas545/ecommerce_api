from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import chat.routing
import notifications.routing
from core.jwt_auth_socket import JwtTokenAuthMiddleware


application = ProtocolTypeRouter(
    {
        # (http->django views is added by default)
        "websocket": JwtTokenAuthMiddleware(
            URLRouter(
                chat.routing.websocket_urlpatterns
                + notifications.routing.websocket_urlpatterns
            )
        )
    }
)

