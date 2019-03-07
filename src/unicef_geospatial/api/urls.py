from django.urls import include, path, re_path

from rest_framework.routers import DefaultRouter

from .openapi import schema_view  # noqa

app_name = 'api'

router = DefaultRouter()

urlpatterns = [
    re_path(r'(?P<version>(v1|latest))/', include(router.urls)),
    path(r'+swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path(r'+redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
