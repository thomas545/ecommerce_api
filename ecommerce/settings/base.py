import datetime
import os

from decouple import config


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


SECRET_KEY = config('SECRET_KEY')


DEBUG = True

ALLOWED_HOSTS = ['*']



INSTALLED_APPS = [
    'jet.dashboard',
    'jet',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    'rest_framework',
    'django_filters',
    'rest_auth',
    'allauth',
    'allauth.account',
    'rest_auth.registration',

    'allauth.socialaccount',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.twitter',

    'phonenumber_field',
    'django_countries',
    'mptt',
    'fcm_django',
    'randompinfield',
    'django_crontab',
    'channels',
    'django_elasticsearch_dsl',
    'django_elasticsearch_dsl_drf',

    'chat',
    'checkout',
    'order',
    'notifications',
    'products',
    'cart',
    'user_profile',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'core.middlewares.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'core.middlewares.FetchFromCacheMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.common.BrokenLinkEmailsMiddleware',
    'django.middleware.locale.LocaleMiddleware'
]

ROOT_URLCONF = 'ecommerce.urls'

TEMPLATE_DIRES = os.path.join(BASE_DIR, 'templates')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIRES],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ecommerce.wsgi.application'

CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = 3600   # this number equal 1h
CACHE_MIDDLEWARE_KEY_PREFIX = ''

# channels redis layers config.
ASGI_APPLICATION = "ecommerce.routing.application"

# CHANNEL_LAYERS = {
#     'default': {
#         'BACKEND': 'channels_redis.core.RedisChannelLayer',
#         'CONFIG': {
#             "hosts": [('127.0.0.1', 6379)],
#         },
#     },
# }
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [os.environ.get('REDIS_URL', 'redis://localhost:6379')],
        },
    },
}


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]



REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 10
}

# Elasticsearch configuration
ELASTICSEARCH_DSL = {
    'default': {
        'hosts': 'localhost:9200'
    },
}

# HAYSTACK_CONNECTIONS = {
#     'default': {
#         'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
#         'URL': 'http://localhost:9200/',
#         'INDEX_NAME': 'products',
#     },
# }
# from elasticsearch_dsl import connections

# connections.configure(
#     default={'hosts': 'localhost'},
#     dev={
#         'hosts': ['localhost:9200'],
#         'sniff_on_start': True
#     }
# )
# # Name of the Elasticsearch index
# ELASTICSEARCH_INDEX_NAMES = {
#     'products/documents/product': 'products',
# }

ELASTICSEARCH_DSL_SIGNAL_PROCESSOR = 'django_elasticsearch_dsl.signals.RealTimeSignalProcessor'

# Rest Auth configuration
JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=30),
    'JWT_ALLOW_REFRESH': True,
    'JWT_REFRESH_EXPIRATION_DELTA': datetime.timedelta(days=100),
}

REST_AUTH_SERIALIZERS = {
    'LOGIN_SERIALIZER': 'user_profile.serializers.LoginSerializer',
    'USER_DETAILS_SERIALIZER': 'user_profile.serializers.UserSerializer',
}
REST_AUTH_REGISTER_SERIALIZERS = {
    'REGISTER_SERIALIZER': 'user_profile.serializers.CustomRegisterSerializer'
}

# FCM (push notifications) configuration
FCM_DJANGO_SETTINGS = {
        "FCM_SERVER_KEY": config("FCM_SERVER_KEY"),
         # true if you want to have only one active device per registered user at a time
         # default: False
        "ONE_DEVICE_PER_USER": True,
         # devices to which notifications cannot be sent,
         # are deleted upon receiving error response from FCM
         # default: False
        "DELETE_INACTIVE_DEVICES": False,
}

REST_USE_JWT = True
SITE_ID = 1

# ACCOUNT_EMAIL_VERIFICATION SETTINGS
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_EMAIL_REQUIRED = True

AUTHENTICATION_BACKENDS = (
    # default
    'django.contrib.auth.backends.ModelBackend',
    # email login
    "user_profile.auth_backends.EmailBackend",
)

# Internationalization

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Phone number country settings
PHONENUMBER_DEFAULT_REGION = 'EG'
PHONENUMBER_DB_FORMAT = 'INTERNATIONAL'

# TWILIO SETTINGS
TWILIO_ACCOUNT_SID = config('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = config('TWILIO_TOKEN')
TWILIO_FROM_NUMBER = config('TWILIO_FROM')


# Celery Settings
# CELERY_BROKER_URL = 'redis://localhost:6379'
# CELERY_RESULT_BACKEND = 'redis://localhost:6379'
# CELERY_ACCEPT_CONTENT = ['application/json']
# CELERY_RESULT_SERIALIZER = 'json'
# CELERY_TASK_SERIALIZER = 'json'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
# STATICFILES_DIRS = [os.path.join(BASE_DIR, "static"),]
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# for cron jobs
from . import cron_jobs
CRONJOBS = cron_jobs.CRONJOBS 
