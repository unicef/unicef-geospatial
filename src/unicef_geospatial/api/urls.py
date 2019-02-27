from django.urls import include, re_path

from rest_framework.routers import DefaultRouter

app_name = 'api'

router = DefaultRouter()

urlpatterns = [
    re_path(r'(?P<version>(v1|latest))/', include(router.urls)),
]
