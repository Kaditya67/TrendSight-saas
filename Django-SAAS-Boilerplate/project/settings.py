"""
Django settings for project project.

Generated by 'django-admin startproject' using Django 4.2.11.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

import os
import json
import base64
import environ
 
import dj_database_url
from email.headerregistry import Address
from django.utils.translation import gettext_lazy as _

from django.templatetags.static import static
from django.urls import reverse_lazy
from unfold.settings import CONFIG_DEFAULTS as UNFOLD_DEFAULTS

from google.oauth2 import service_account

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))
# print(env('DEBUG'))

cloud_platform = os.environ.setdefault('CLOUD_PLATFORM', '')

# FIREBASE_CRED_PATH = env('FIREBASE_CRED_PATH')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
if DEBUG:
    SECRET_KEY = env.get_value('SECRET_KEY', default='django-insecure-ksgg^#ftx9*t8rh0e*y+j=g1m&&i8(-3nh*tm(at@s7^#j_8g1mnn')

else:
    SECRET_KEY = env.get_value('PORD_SECRET_KEY')


if not DEBUG and cloud_platform in ['DIGITAL_OCEAN', 'RAILWAY']:
    # since the firebase-cred cannot be uploaded manually 
    # https://www.digitalocean.com/community/questions/how-to-upload-a-secret-credential-file
    firebase_cred = env('FIREBASE_ENCODED')
    decoded_bytes = base64.b64decode(firebase_cred)
    decoded_json = json.loads(decoded_bytes.decode('utf-8'))
  
    with open(FIREBASE_CRED_PATH, 'w') as f:
        json.dump(decoded_json, f, indent=4)

if DEBUG:
    ALLOWED_HOSTS = []

else:
    ALLOWED_HOSTS = env('ALLOWED_HOSTS').replace(' ', '').split(',')

if not DEBUG:
    CORS_ALLOWED_ORIGINS = env('ALLOWED_CORS').replace(' ', '').split(',')

    CORS_ORIGIN_WHITELIST = env('ALLOWED_CORS').replace(' ', '').split(',')
    CSRF_TRUSTED_ORIGINS = env('ALLOWED_CORS').replace(' ', '').split(',')


PROJECT_TITLE = 'Saas Django demo' # name of the project

if DEBUG:
    DOMAIN = "http://localhost:8000"

else:
    DOMAIN = env('DOMAIN')


# Application definition

INSTALLED_APPS = [

    'unfold', # django unfold admin
    "unfold.contrib.forms",

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django.contrib.sites',  # sitemaps 
    'django.contrib.sitemaps',  # sitemaps 


    # 3rd party
    'tailwind',
    'corsheaders',
    'payments',
    'django_browser_reload',

    'styling',

    #first party
    'user',
    'blog',
    'inquiry',
    'transaction',
    'stocks',
]

if not DEBUG:
    INSTALLED_APPS += ['anymail'] 

SITE_ID = 1 # for sitemaps
# ANALYTICS_TAG_ID = env('GOOGLE_ANALYTICS') # for analytics tag on frontend

AUTH_USER_MODEL = "user.User" 

LOGIN_URL = '/user/login/'
LOGIN_REDIRECT_URL = '/'

TAILWIND_APP_NAME = 'styling'


INTERNAL_IPS = [
    "127.0.0.1",
]

PAYMENT_MODEL = 'transaction.Transaction'

if DEBUG:
    PAYMENT_HOST = 'localhost:8000'

    # Whether to use TLS (HTTPS). If false, will use plain-text HTTP.
    # Defaults to ``not settings.DEBUG``.
    PAYMENT_USES_SSL = False

   

# Settings for Development
PAYMENT_VARIANTS = {
    'stripe': (
        # 'payments.stripe.StripeProviderV3',
        'payments.stripe.StripeProvider',
        {
            'api_key': env('STRIPE_TEST_API_KEY'),
            'use_token': True,
            'secure_endpoint': False,
            'secret_key': env('STRIPE_TEST_API_KEY'),
            'public_key': env('STRIPE_PUB_TEST_KEY'),
            'endpoint_secret': env('STRIPE_WEBHOOK_TEST_API_KEY'),
        }
    )
}

 # Settings for Production
    # PAYMENT_VARIANTS = {
    #     'stripe': (
    # #        'payments.stripe.StripeProviderV3',
    #    'payments.stripe.StripeProvider',
    #         {
    #             'use_token': True,
    #             'secure_endpoint': True
    #             'secret_key': env('STRIPE_TEST_API_KEY'),
    #             'public_key': env('STRIPE_PUB_TEST_KEY'),
    #              'endpoint_secret': env('STRIPE_WEBHOOK_TEST_API_KEY'),
    #         }
    #     )
    # }

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'whitenoise.middleware.WhiteNoiseMiddleware', #whitenoise
    'django_browser_reload.middleware.BrowserReloadMiddleware', # reload
    'django_ratelimit.middleware.RatelimitMiddleware',
]

ROOT_URLCONF = 'project.urls'

if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' # This is only for development
    # EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'

else: 
    EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend' # This is only for development

    # uncomment below for default production emailing
    # EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend' # for production

    # EMAIL_HOST = env('EMAIL_HOST') #eg: smtpout.secureserver.net
    # EMAIL_PORT = 465

    # EMAIL_HOST_USER = env('EMAIL_HOST_USER') # eg: info@mail.com
    # EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')

    # DEFAULT_FROM_EMAIL = Address(display_name=env('EMAIL_HOST_USER'), addr_spec=EMAIL_HOST_USER)

    # EMAIL_USE_SSL = True

    # uncomment below for ESP, read: https://dev.to/paul_freeman/adding-esp-to-supercharge-your-django-email-4jkp

    # EMAIL_BACKEND = "anymail.backends.brevo.EmailBackend"
        
    # BREVO_API_URL = "https://api.brevo.com/v3/"
    
    # ANYMAIL = {
    #         "BREVO_API_KEY": env('BREVO_API_KEY'), # use brevo api key instead of smtp key 
    #         "IGNORE_RECIPIENT_STATUS": True,
    #     }
    # DEFAULT_FROM_EMAIL = env('EMAIL_HOST_USER')  # default from email


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR.joinpath("templates"),
            BASE_DIR.joinpath("templates", "html"),
            BASE_DIR.joinpath("templates", "html", "error"),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'libraries':{
                'custom_tags': 'project.templatetags.custom_tags',
            }
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        },
        'OPTIONS': {
            "timeout": 20,
        }
    }

else:
    # DATABASES = {
    #         'default': {
    #             'ENGINE': 'django.db.backends.postgresql_psycopg2',
    #             'NAME': env.get_value('POSTGRES_DATABASE'), # use env file
    #             'USER': env.get_value('POSTGRES_USER'),
    #             'PASSWORD': env.get_value('POSTGRES_PASSWORD'),
    #             'HOST': env.get_value('POSTGRES_HOST'),
    #             'PORT': '5432',
    #     }
    # }

    DATABASES  = {
                    'default':dj_database_url.config(default=env('POSTGRES_URL')),   
                }
    DATABASES['default']['ENGINE'] = 'django.db.backends.postgresql_psycopg2'


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# STATIC_ROOT = BASE_DIR.joinpath('staticfiles', 'static')
STATICFILES_DIRS = [
    BASE_DIR.joinpath('staticfiles', 'static'),
    BASE_DIR.joinpath('templates'),
    BASE_DIR.joinpath('templates', 'assets'),
] 

MEDIA_ROOT = BASE_DIR.joinpath('media')


if DEBUG:
    MEDIA_URL = '/media/'
    MEDIA_DOMAIN = 'http://localhost:8000'
   
else:
    MEDIA_URL = '/media/'

    # Define the storage settings for media files
    DEFAULT_FILE_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
    GS_BUCKET_NAME = env("BUCKET_NAME") # google storage - GS
    GS_PROJECT_ID = env("PROJECT_ID")
    GS_CREDENTIALS = service_account.Credentials.from_service_account_file(
        BASE_DIR.joinpath(env("FIREBASE_CRED_PATH"))
    )
    GS_DEFAULT_ACL = "publicRead"  # Optional: Set ACL for public access
    GS_QUERYSTRING_AUTH = True  # Optional: Enable querystring authentication
    GS_FILE_OVERWRITE = False # prevent overwriting


# Unfold
######################################################################
UNFOLD = {
    "SITE_HEADER": _("Admin"),
    "SITE_TITLE": _("Admin"),
    "SITE_SYMBOL": "settings",
    "SHOW_HISTORY": True,
    "DASHBOARD_CALLBACK": "project.views.dashboard_callback",
    "LOGIN": {
        "image": lambda request: static("images/login-bg.jpg"),
    },
    "STYLES": [
        lambda request: static("css/unfold-admin.css"),
    ],
    "SCRIPTS": [
    ],
    "COLORS": {
        "primary": {
            "50": "250 245 255",
            "100": "243 232 255",
            "200": "233 213 255",
            "300": "216 180 254",
            "400": "192 132 252",
            "500": "168 85 247",
            "600": "147 51 234",
            "700": "126 34 206",
            "800": "107 33 168",
            "900": "88 28 135",
            "950": "59 7 100",
        },
    },
   
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": _("Navigation"),
                "items": [

                    {
                        "title": _("Dashboard"),
                        "icon": "dashboard",
                        "link": reverse_lazy("admin:index"), 
                    },
                    {
                        "title": _("Blogs"),
                        "icon": "Wysiwyg",
                        "link": reverse_lazy("admin:blog_blog_changelist"), # default: admin:myapp_mymodel_changelist
                    },
                    {
                        "title": _("Inquires"),
                        "icon": "person_raised_hand",
                        "link": reverse_lazy("admin:inquiry_inquiry_changelist"), # default: admin:myapp_mymodel_changelist
                    },
                  
                    
                ],
            },
            {
                "title": _("Plans and Transactions"),
                "separator": True,
                "items": [
                    {
                        "title": _("Plan"),
                        "icon": "description",
                        "link": reverse_lazy("admin:transaction_plan_changelist"),
                    },
                    {
                        "title": _("Transactions"),
                        "icon": "payments",
                        "link": reverse_lazy("admin:transaction_transaction_changelist"),
                    },
                ],
            },
            {
                "title": _("Users and Permission"),
                "separator": True,
                "items": [
                    {
                        "title": _("Users"),
                        "icon": "person",
                        "link": reverse_lazy("admin:user_user_changelist"),
                    },
                    {
                        "title": _("Groups"),
                        "icon": "group",
                        "link": reverse_lazy("admin:auth_group_changelist"),
                    },
                ],
            },
           
        ],
    },
}



LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'verbose': {
            'format': '[contactor] %(levelname)s %(asctime)s %(message)s'
        },
    },
    'handlers': {
        # Send all messages to console
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
        
        'celery': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },

        # Send info messages to syslog
        # 'syslog':{
        #     'level':'INFO',
        #     'class': 'logging.handlers.SysLogHandler',
        #     'facility': SysLogHandler.LOG_LOCAL2,
        #     'address': '/dev/log',
        #     'formatter': 'verbose',
        # },
        # Warning messages are sent to admin emails
        'mail_admins': {
            'level': 'WARNING',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        },
    },
    'loggers': {
        # This is the "catch all" logger
        '': {
            'handlers': ['console', 'mail_admins', 'celery'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}