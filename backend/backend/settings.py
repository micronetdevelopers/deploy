

from pathlib import Path
import os
from datetime import timedelta
import environ
from environ import Env

env = Env(
    # set casting, default value
    DEBUG=(bool, False)
)
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# env = Env()
env.read_env(BASE_DIR / '.env')

# Assuming this file is in the root of your project directory

# Append the project root to sys.path

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-gjfyu@1-p1xr_sxj8o5$2l4$qdx81j^vw6=1$^2s)5im68ck4!'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# settings.py

# ALLOWED_HOSTS = ['13.233.146.103', '127.0.0.1', 'localhost']
ALLOWED_HOSTS = ["127.0.0.1", ".vercel.app", ".now.sh"]

CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]

AUTH_USER_MODEL = 'authentification.User_login_Data'

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'auditlog',
    'rest_framework',
    'authentification.apps.AuthentificationConfig',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'archival',
    'search',
   
]

# CORS_ORIGIN_ALLOW_ALL = True

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',  # for session-based authentication
        'rest_framework.authentication.TokenAuthentication',    # for token-based authentication
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS':'rest_framework.schemas.coreapi.AutoSchema',
    'DEFAULT_PERMISSION_CLASSES':[
        'rest_framework.permissions.AllowAny',
    ]
}

# from .myapp.middleware import SuperuserMiddleware

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'authentification.login_file.SuperuserMiddleware',
    # 'authentification.middleware.log.simple_middleware',
    'authentification.middleware.log.MyMiddleware',
    'auditlog.middleware.AuditlogMiddleware',
    
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'build')],
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

WSGI_APPLICATION = 'backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {

    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'GEOPICX',
        'USER': 'postgres',
        'HOST': 'localhost',
        'PASSWORD': 'Abcd@1234',
        'PORT': '5432',
        # 'ENGINE': 'django.db.backends.postgresql_psycopg2',
        # 'NAME': '<mydb>',
        # 'USER': '<myuser>',
        # 'PASSWORD': '<mypass>',
        # 'HOST': 'localhost',
        # 'PORT': '5432',
    }
}

# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:3000",  # Replace with the URL of your React app
#     # Add other allowed origins as needed
# ]

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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



# Django project settings.py

from datetime import timedelta
...

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=5),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": False,

    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": "",
    "AUDIENCE": None,
    "ISSUER": None,
    "JSON_ENCODER": None,
    "JWK_URL": None,
    "LEEWAY": 0,

    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",

    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",

    "JTI_CLAIM": "jti",

    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),

    "TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainPairSerializer",
    "TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSerializer",
    "TOKEN_VERIFY_SERIALIZER": "rest_framework_simplejwt.serializers.TokenVerifySerializer",
    "TOKEN_BLACKLIST_SERIALIZER": "rest_framework_simplejwt.serializers.TokenBlacklistSerializer",
    "SLIDING_TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainSlidingSerializer",
    "SLIDING_TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSlidingSerializer",
}








# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

# BASE_DIR1 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


STATIC_URL = '/static/'
print("STATIC_URL" ,STATIC_URL)

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
# # Define the path to the static files directory
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'build', 'static'),
]
print("STATICFILES_DIRS ",STATICFILES_DIRS)



# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'bhushan.microdev02@gmail.com'
EMAIL_HOST_PASSWORD = 'rwkj sexm bzjp htmc'
EMAIL_USE_TLS = True

AUDITLOG_INCLUDE_ALL_MODELS=True

# django-auditlog
# Mailtrap Email Sending,
#django-simple-history
#Simple-history
# ==================================logs impliment======================
import os

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "class": "logging.FileHandler",
            "filename":env('DJANGO_LOG_FILE'),     #"general.log",
            "level":env('DJANGO_LOG_LEVEL'),   #"DEBUG",
            "formatter": "verbose"   #simple
        },
        "console": {
            "class": "logging.StreamHandler",
            "level":env('DJANGO_LOG_LEVEL'),            #"DEBUG",
            "formatter": "simple"
        },
    },
    "loggers":{
        "":{
            "level":env('DJANGO_LOG_LEVEL'),              #"DEBUG",
            "handlers": ["file", "console"]
        }
    },

    "formatters": {
        "simple": {
            "format": "{asctime}:{levelname} - {name} {module}.py (line {lineno:d}). {message}",
            "style" : "{"
        },
        "verbose": {
            "format": "{asctime}:{levelname} - {name} {module}.py (line {lineno:d}). {message}",
            "style": "{",
        },
    }
}