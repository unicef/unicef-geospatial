import os
from pathlib import Path

import environ

SETTINGS_DIR = Path(__file__).parent
PACKAGE_DIR = SETTINGS_DIR.parent
DEVELOPMENT_DIR = PACKAGE_DIR.parent.parent

env = environ.Env(
    AZURE_CLIENT_ID=(str, ''),
    AZURE_CLIENT_SECRET=(str, ''),
    AZURE_TENANT=(str, ''),
    SECRET_KEY=(str, 'lkjokjlokjlkj'),
    DATABASE_URL=(str, "postgis://postgres:@127.0.0.1:5432/geospatial"),
    CACHE_URL=(str, "dummycache://"),
    CACHE_URL_LOCK=(str, "dummycache://"),
    STATIC_ROOT=(str, "/tmp/"),
)

SECRET_KEY = env('SECRET_KEY')

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
    'crashlog',
    'constance',
    'django_fsm',
    'django_fsm_log',
    'admin_extra_urls',
    'impersonate',
    'rest_framework',
    'django_admin_json_editor',
    'unicef_geospatial.core.apps.Config',
    'unicef_geospatial.web.apps.Config',
)
# DJANGO: SECURITY
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
]

DEBUG = True

# ORIGINAL_BACKEND = 'django.contrib.gis.db.backends.postgis'
DATABASES = {
    'default': env.db()
}
DATABASES['default']['USER'] = 'postgres'
DATABASES['default']['NAME'] = 'geospatial'

MEDIA_ROOT = os.environ.get('MEDIA_ROOT', '/tmp/geospatial/media/')
MEDIA_URL = '/media/'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'unicef_geospatial.state.middleware.StateMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
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
                #                'social_django.context_processors.backends',
                #                'social_django.context_processors.login_redirect',
                'unicef_geospatial.web.context_processors.sett',
                'unicef_geospatial.state.context_processors.state',

            ],
        },
    },
]

CACHES = {
    'default': env.cache(),
    'lock': env.cache('CACHE_URL_LOCK'),
}

# DJANGO: URLS
ROOT_URLCONF = 'unicef_geospatial.config.urls'

# CONTRIB: AUTH
AUTHENTICATION_BACKENDS = (
    # 'social_core.backends.azuread_tenant.AzureADTenantOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)
# AUTH_USER_MODEL = 'unicef_security.User'

LOGIN_REDIRECT_URL = '/'

HOST = 'localhost:8000'

# CONTRIB: STATIC FILES
STATIC_URL = '/static/'
STATIC_ROOT = env('STATIC_ROOT')
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
    'ATTRIBUTION_PREFIX': 'Tiles &copy; Esri &mdash; Source: Esri, DeLorme, NAVTEQ, USGS, Intermap, iPC, NRCAN, Esri Japan, METI, Esri China (Hong Kong), Esri (Thailand), TomTom, 2012',
    # noqa
    'MIN_ZOOM': 3,
    'MAX_ZOOM': 18,
}

CONSTANCE_ADDITIONAL_FIELDS = {
    'select_group': ['unicef_geospatial.utils.constance.GroupChoiceField', {
        'required': False,
        'widget': 'unicef_geospatial.utils.constance.GroupChoice',
    }],
}

CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'
CONSTANCE_CONFIG = {
    'CACHE_VERSION': (1, '', int),
    'DEFAULT_GROUP': ('Guests', 'Default group new users belong to', 'select_group'),
    'LOADER_MANDATORY_FIELDS': ('', 'Comma separated list of fields than MUST exists en each shapefile', str)

}

DATA_SCHEMA = {
    'type': 'object',
    'title': 'Data',
    'properties': {
        'text': {
            'title': 'Some text',
            'type': 'string',
            'format': 'textarea',
        },
        'status': {
            'title': 'Status',
            'type': 'boolean',
        },
    },
}

SOCIAL_AUTH_POSTGRES_JSONFIELD = True
SOCIAL_AUTH_USERNAME_IS_FULL_EMAIL = False
SOCIAL_AUTH_PROTECTED_USER_FIELDS = ['username']
SOCIAL_AUTH_SANITIZE_REDIRECTS = False
SOCIAL_AUTH_URL_NAMESPACE = 'social'
SOCIAL_AUTH_WHITELISTED_DOMAINS = ['unicef.org', ]
SOCIAL_AUTH_REVOKE_TOKENS_ON_DISCONNECT = True
SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
    'social_core.pipeline.social_auth.associate_by_email',
)
SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_KEY = env.str('AZURE_CLIENT_ID')
SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_SECRET = env.str('AZURE_CLIENT_SECRET')
SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_TENANT_ID = env.str('AZURE_TENANT')
SOCIAL_AUTH_AZUREAD_OAUTH2_KEY = env.str('AZURE_CLIENT_ID')
SOCIAL_AUTH_AZUREAD_OAUTH2_RESOURCE = 'https://graph.microsoft.com/'
