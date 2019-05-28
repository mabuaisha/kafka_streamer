from .base import *

import dj_database_url

DEBUG = True

TEMPLATES[0]['OPTIONS']['debug'] = DEBUG

WSGI_APPLICATION = 'wsgi.local.application'

MIDDLEWARE += ('debug_toolbar.middleware.DebugToolbarMiddleware', )

INSTALLED_APPS += ('debug_toolbar', )

SECRET_KEY = 'ui9hb!-_0shivrh1xtztinys)ya$lm$0xvh*_zbdydc-pdn3$y'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
}

# DATABASE_URL = os.environ['DATABASE_URL']
# DATABASES = {
#     'default': dj_database_url.parse(DATABASE_URL),
# }
#
# DATABASES['default']['CONN_MAX_AGE'] = None

DEFAULT_FILE_STORAGE = u'storages.backends.overwrite.OverwriteStorage'
PIPELINE['PIPELINE_ENABLED'] = False
