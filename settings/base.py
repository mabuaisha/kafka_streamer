"""
Django settings for kafka_streamer project.

Generated by 'django-admin startproject' using Django 2.2.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'pipeline',
    'storages',
    'pubsub'
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'root': {
        'level': 'INFO',
        'handlers': ['console', ],
        'formatters': ['simple', ],
    },

    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(name)s: %(message)s',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'kafka': {
            'handlers': ['console'],
            'level': 'INFO',
        }
    }
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/
AWS_CLOUDFRONT_DOMAIN = os.environ.get('AWS_CLOUDFRONT_DOMAIN')

STATIC_URL = os.environ.get('STATIC_URL', '/static/')
STATIC_ROOT = os.path.join(BASE_DIR, '.static')
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

# Configuration for django-storages to use S3
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', '')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME', '')

AWS_S3_SECURE_URLS = True
AWS_REDUCED_REDUNDANCY = False
AWS_PRELOAD_METADATA = True
AWS_IS_GZIPPED = True
AWS_AUTO_CREATE_BUCKET = True
AWS_QUERYSTRING_AUTH = False
AWS_S3_FILE_OVERWRITE = True

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

GZIP_CONTENT_TYPES = (
    'text/css',
    'application/javascript',
    'application/x-javascript',
)

PIPELINE = {
    'PIPELINE_ENABLED': True,
    'CSS_COMPRESSOR': None,
    'JS_COMPRESSOR': None,
}

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'pipeline.finders.CachedFileFinder',
    'pipeline.finders.PipelineFinder',
)


# Kafka Settings
CLOUDKARAFKA_BROKERS = os.environ['CLOUDKARAFKA_BROKERS']
CLOUDKARAFKA_USERNAME = os.environ['CLOUDKARAFKA_USERNAME']
CLOUDKARAFKA_PASSWORD = os.environ['CLOUDKARAFKA_PASSWORD']
CLOUDKARAFKA_TIMEOUT = os.environ.get('CLOUDKARAFKA_TIMEOUT', 6000)
CLOUDKARAFKA_PROTOCOL = os.environ.get('CLOUDKARAFKA_PROTOCOL', 'SASL_SSL')
CLOUDKARAFKA_MECHANISMS = os.environ.get('CLOUDKARAFKA_PROTOCOL',
                                         'SCRAM-SHA-256')

CLOUDKARAFKA_TOPIC_CONFIG = {
    'auto.offset.reset': 'smallest'
}

# KAFKA TOPICS
CLOUDKARAFKA_TOPIC_OSM = os.environ.get('CLOUDKARAFKA_TOPIC_OSM')
CLOUDKARAFKA_TOPIC_GEONAMES = os.environ.get('CLOUDKARAFKA_TOPIC_GEONAMES')
CLOUDKARAFKA_TOPIC_SCHOOL = os.environ.get('CLOUDKARAFKA_TOPIC_SCHOOL')
CLOUDKARAFKA_TOPIC_WIKI = os.environ.get('CLOUDKARAFKA_TOPIC_WIKI')

# Instagram config
INSTAGRAM_CLIENT_ID = os.environ.get('INSTAGRAM_CLIENT_ID')
INSTAGRAM_CLIENT_SECRET = os.environ.get('INSTAGRAM_CLIENT_SECRET')
INSTAGRAM_ACCESS_TOKEN = os.environ.get('INSTAGRAM_ACCESS_TOKEN')
INSTAGRAM_CODE = os.environ.get('INSTAGRAM_CODE')
