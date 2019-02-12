from rest_framework.viewsets import ReadOnlyModelViewSet
from unicef_geo.libs import serializer_factory

from .models import Location


class LocationViewSet(ReadOnlyModelViewSet):
    queryset = Location.objects.all()
    serializer_class = serializer_factory(Location)
