from django.conf.urls import url
from django.contrib import admin
from django.urls import include, path

import unicef_geospatial.api.urls

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    # path(r's/', include('social_django.urls', namespace='social')),
    path(r'', include('unicef_geospatial.core.urls')),
    path(r'impersonate/', include('impersonate.urls')),
    path(r'api/', include(unicef_geospatial.api.urls), name='api'),

]
