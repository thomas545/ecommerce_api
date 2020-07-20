from .base import *


DEBUG = True

# Email config
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_PORT = config('EMAIL_PORT', cast=int, default=587)
EMAIL_USE_TLS = True


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postresql',
        'NAME': config('DATABASE_NAME'),
        'USER': config('DATABASE_USER'),
        'PASSWORD': config('DATABASE_PASSWORD'),
        'HOST': config('DATABASE_HOST')
        'PORT': config('DATABASE_PORT')
    }
}



# Configure as cache backend (Redis)
'''
redis://: creates a normal TCP socket connection
rediss://: creates a SSL wrapped TCP socket connection
unix:// creates a Unix Domain Socket connection
'''
# CACHES = {
#     "default": {
#         "BACKEND": "django_redis.cache.RedisCache",
#         "LOCATION": "redis://127.0.0.1:6379/1",
#         "OPTIONS": {
#             "CLIENT_CLASS": "django_redis.client.DefaultClient",
#             "SERIALIZER": "django_redis.serializers.json.JSONSerializer",
#         }
#     }
# }
