from django.contrib.gis.db.models import MultiPolygonField
from django.db import models
from django.utils.translation import ugettext_lazy as _

from unicef_geo.models import AbstractGeoModel


class AdminBoundary(AbstractGeoModel):

    COD = 'cod'
    GLOBAL = 'global'

    GENDER = (
        (COD, 'COD'),
        (GLOBAL, 'Global'),
    )

    geom = MultiPolygonField(verbose_name=_("Geometry"), null=True, blank=True, spatial_index=True)
    gender = models.CharField(max_length=15, choices=GENDER)

    class Meta:
        verbose_name_plural = _('Admin Boundaries')
