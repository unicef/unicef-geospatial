import os
from os.path import abspath, dirname, join, normpath

import dj_database_url

SECRET_KEY = r'geo_spacial_asfbjdlksangds'


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'django.contrib.postgres',
    'django.contrib.admin',
    'django.contrib.humanize',
    'mptt',
    'leaflet',
    'unicef_geo.boundaries',
    'unicef_geo.categories',
    'unicef_geo.countries',
    'unicef_geo.locations',
    'unicef_geospatial.apps.core',
)
# DJANGO: SECURITY
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
]

DEBUG = True

CONFIG_ROOT = dirname(dirname(abspath(__file__)))

db_config = dj_database_url.config(default='postgis:///geospacial')

ORIGINAL_BACKEND = 'django.contrib.gis.db.backends.postgis'
db_config['CONN_MAX_AGE'] = 0
DATABASES = {
    'default': db_config
}
DATABASES['default']['USER'] = 'postgres'
DATABASES['default']['NAME'] = 'geospacial'

MEDIA_ROOT = os.environ.get('MEDIA_ROOT', '/tmp/geospacial/media/')
MEDIA_URL = '/media/'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'corsheaders.middleware.CorsMiddleware',
)
WSGI_APPLICATION = 'unicef_geospatial.config.wsgi.application'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
        ],
        'OPTIONS': {
            'debug': DEBUG,
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
            'context_processors': [
                # Already defined Django-related contexts here
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.request',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',

            ],
        },
    },
]
# DJANGO: URLS
ROOT_URLCONF = 'unicef_geospatial.config.urls'

# CONTRIB: AUTH
AUTHENTICATION_BACKENDS = (
    # 'social_core.backends.azuread_b2c.AzureADB2COAuth2',
    'django.contrib.auth.backends.ModelBackend',
)
# AUTH_USER_MODEL = 'users.User'

LOGIN_REDIRECT_URL = '/'

HOST = 'localhost:8000'

# CONTRIB: STATIC FILES
STATIC_URL = '/static/'
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
    ),
    'TEST_REQUEST_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.MultiPartRenderer',
    ),
}

LEAFLET_CONFIG = {
    'TILES': 'http://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}',
    'ATTRIBUTION_PREFIX': 'Tiles &copy; Esri &mdash; Source: Esri, DeLorme, NAVTEQ, USGS, Intermap, iPC, NRCAN, Esri Japan, METI, Esri China (Hong Kong), Esri (Thailand), TomTom, 2012',  # noqa
    'MIN_ZOOM': 3,
    'MAX_ZOOM': 18,
}
