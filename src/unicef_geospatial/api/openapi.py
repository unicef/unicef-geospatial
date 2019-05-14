# flake8: noqa E501

from drf_yasg import openapi
from drf_yasg.app_settings import swagger_settings
from drf_yasg.views import get_schema_view
from rest_framework import permissions

description = """
""".format(HOST=swagger_settings.DEFAULT_API_URL)

schema_view = get_schema_view(
    openapi.Info(
        title="Geospatial Datamart API",
        default_version='v1',
        description=description,
        # terms_of_service="https://",
        # contact=openapi.Contact(email="contact@snippets.local"),
        # license=openapi.License(name="BSD License"),
        # aaaaaaa="aaaaaa",
    ),
    # validators=['flex', 'ssv'],
    public=True,
    permission_classes=(permissions.AllowAny,),
)
