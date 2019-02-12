from rest_framework.viewsets import ReadOnlyModelViewSet
from unicef_geo.libs import serializer_factory

from .models import AdminBoundary


class AdminBoundaryViewSet(ReadOnlyModelViewSet):
    queryset = AdminBoundary.objects.all()
    serializer_class = serializer_factory(AdminBoundary)
