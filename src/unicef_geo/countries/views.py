from rest_framework.viewsets import ReadOnlyModelViewSet
from unicef_geo.libs import serializer_factory

from .models import Country


class CountryViewSet(ReadOnlyModelViewSet):
    queryset = Country.objects.all()
    serializer_class = serializer_factory(Country)
