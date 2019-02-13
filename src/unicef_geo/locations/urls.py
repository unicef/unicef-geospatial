from django.conf.urls import include, url

from rest_framework import routers

from . import views

app_name = 'locations'

api = routers.SimpleRouter()

api.register(r'locations', views.LocationViewSet, base_name='locations')

urlpatterns = [
    url(r'', include(api.urls)),
]
