from django.conf.urls import include, url

urlpatterns = [
    url(r'^boundaries/', include('unicef_geo.boundaries.urls')),
    url(r'^categories/', include('unicef_geo.categories.urls')),
    url(r'^countries/', include('unicef_geo.countries.urls')),
    url(r'^locations/', include('unicef_geo.locations.urls')),
]
