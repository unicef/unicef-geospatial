from django.conf.urls import include, url

from rest_framework import routers

from .views import CountryViewSet

app_name = 'unicef_geo'

api = routers.SimpleRouter()

api.register(r'countries', CountryViewSet, base_name='country')


urlpatterns = [
    url(r'', include(api.urls)),
]
