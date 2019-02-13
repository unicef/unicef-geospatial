from django.conf.urls import include, url

from rest_framework import routers

from .views import AdminBoundaryViewSet

app_name = 'boundaries'

api = routers.SimpleRouter()

api.register(r'boundaries', AdminBoundaryViewSet, base_name='boundary')


urlpatterns = [
    url(r'', include(api.urls)),
]
