"""
Django settings for wrh_organization project.

Generated by 'django-admin startproject' using Django 4.0.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""
from datetime import timedelta
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

EXTERNAL_CONFIG_PATH = '/opt/webapps/wrh_organization/etc/external_config.py'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'SECRET_KEY'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third Party Apps
    'dbbackup',
    'django_filters',
    'storages',
    'rest_framework',
    # Project Apps
    'apps.account',
    'apps.bycing_org',
    'apps.usacycling'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'wrh_organization.helpers.middleware.DisableCSRFMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'wrh_organization.helpers.middleware.InjectUiVersionInHeadersMiddleware',
    'wrh_organization.helpers.middleware.ThreadLocalMiddleware',
]

ROOT_URLCONF = 'wrh_organization.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'wrh_organization' / 'templates',],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
            ],
            'libraries': {
                'util_tags': 'wrh_organization.templatetags.util_tags',
            }
        },
    },
]

WSGI_APPLICATION = 'wrh_organization.wsgi.application'
ASGI_APPLICATION = 'wrh_organization.asgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'wrh_organization',
        'HOST': '127.0.0.1',
        'PORT': '5432',
        'USER': 'postgres',
        'PASSWORD': 'a',
    }
}

DOMAIN = 'localhost'

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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


CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
CSRF_DISABLED = False  # disable checking csrf. warning!!! this should be set to False in production

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

DATA_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024  # 50 MB

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/
VUE_STATIC_INDEX = '/static/vue/index.html'
LOGIN_URL = f'{VUE_STATIC_INDEX}#/dashboard/home'

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / "collected_static"

STATICFILES_DIRS = (
    BASE_DIR / "static",
)

MEDIA_URL = '/media/'

MEDIA_ROOT = BASE_DIR / "media"

# # Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'wrh_organization.helpers.utils.custom_rest_exception_handler',
    'DEFAULT_PERMISSION_CLASSES': [
        'wrh_organization.helpers.utils.CustomDjangoModelPermissions'
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'wrh_organization.helpers.utils.NestedMultipartParser'
    ],
    # 'DEFAULT_RENDERER_CLASSES': [
    #     'rest_framework.renderers.JSONRenderer',
    #     'rest_framework.renderers.AdminRenderer',
    #     'rest_framework.renderers.BrowsableAPIRenderer'
    # ],
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning',
    'DEFAULT_VERSION': 'v1',
    'ALLOWED_VERSIONS': ['v1'],
    'VERSION_PARAM': 'version',
    'DEFAULT_PAGINATION_CLASS': 'wrh_organization.helpers.utils.CustomPagination',
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',
                                'rest_framework.filters.SearchFilter',
                                'wrh_organization.helpers.utils.ExtendedOrderingFilterBackend'),
    'PAGE_SIZE': 25,
    'MAX_PAGE_SIZE_DEFAULT': 1000,
    'ORDERING_PARAM': 'order_by',
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=10),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': False,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'JTI_CLAIM': 'jti',
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

# DataFlair #Logging Information
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] %(levelname)s %(pathname)s:%(lineno)d %(message)s'
        },
        'simple': {
            'format': '[%(asctime)s] %(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

AUTH_USER_MODEL='account.User'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.AllowAllUsersModelBackend',
]

# dbbackup settings
DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
DBBACKUP_CONNECTOR_MAPPING = {
    'django.db.backends.postgresql': 'dbbackup.db.postgresql.PgDumpBinaryConnector',
}
DBBACKUP_CONNECTORS = {
    'default': {
        'SINGLE_TRANSACTION': False
    }
}

# AWS s3 storage
AWS_ACCESS_KEY_ID = '<AWS_ACCESS_KEY_ID>'
AWS_SECRET_ACCESS_KEY = '<AWS_SECRET_ACCESS_KEY>'
AWS_STORAGE_BUCKET_NAME = '<AWS_STORAGE_BUCKET_NAME>'
AWS_PUBLIC_STORAGE_BUCKET_NAME = '<AWS_PUBLIC_STORAGE_BUCKET_NAME>'
AWS_S3_FILE_OVERWRITE = True
AWS_DEFAULT_ACL = None
AWS_BUCKET_ACL = None
AWS_AUTO_CREATE_BUCKET = True
AWS_QUERYSTRING_AUTH = True
AWS_QUERYSTRING_EXPIRE = 3600
AWS_S3_REGION_NAME = None
AWS_S3_SIGNATURE_VERSION = None
AWS_MEDIA_LOCATION = 'media'
AWS_STATIC_LOCATION = 'static'
# DEFAULT_FILE_STORAGE = 'wrh_organization.helpers.utils.S3MediaStorage'
# PUBLIC_FILE_STORAGE = 'wrh_organization.helpers.utils.S3PublicMediaStorage'
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
PUBLIC_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}

# email setting
# EMAIL_BACKEND = 'anymail.backends.mailgun.EmailBackend'
EMAIL_BACKEND = 'anymail.backends.sendgrid.EmailBackend'
ANYMAIL = {
    # sendgrid
    'SENDGRID_API_KEY': '<SENDGRID_API_KEY>',

    # mailgun
    'MAILGUN_SENDER_DOMAIN': '<MAILGUN_SENDER_DOMAIN>',
    'MAILGUN_API_KEY': '<MAILGUN_API_KEY>',
}
DEFAULT_EMAIL_FROM = "info@weracehere.org"

# twilio sms setting
SENDSMS_BACKEND = 'wrh_organization.helpers.utils.SmsBackend'
SENDSMS_TWILIO_ACCOUNT_SID = 'SIDXXXXXXXXXXXXXXX'
SENDSMS_TWILIO_AUTH_TOKEN = 'ATXXXXXXXXXXXXXXX'
SMS_DEFAULT_FROM_PHONE = 'NNNNNNNNNN'

# stripe
STRIPE_PUBLISHABLE_KEY = '<STRIPE_PUBLISHABLE_KEY>'
STRIPE_SECRET_KEY = '<STRIPE_SECRET_KEY>'

# project setting
IMAGE_UPLOAD_MAX_SIZE = 2 * 1024 * 1024  # 2 MB
PAGINATION_DEFAULT_PAGINATION = 10
PAGINATION_MAX_SIZE = 200
SIGNUP_ACTIVATION_REDIRECT_URL = '/'
DEFAULT_ORGANIZATION_ID = 1

OTP_MEMBER_VERIFY_KEY = '<OTP_MEMBER_VERIFY_KEY>'
OTP_MEMBER_VERIFY_CODE_LENGTH = 6
OTP_MEMBER_VERIFY_INTERVAL = 120
OTP_MEMBER_VERIFY_VALID_WINDOW = 1
