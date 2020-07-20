from .base import *


DEBUG = True

INSTALLED_APPS += [
    "debug_toolbar",
]

MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


def show_toolbar(request):
    return True


DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": show_toolbar,
}

# Email config
EMAIL_HOST = "smtp.gmail.com"
EMAIL_HOST_USER = "ecommerce@gmail.com"
EMAIL_HOST_PASSWORD = 213123
EMAIL_PORT = 587
EMAIL_USE_TLS = True
