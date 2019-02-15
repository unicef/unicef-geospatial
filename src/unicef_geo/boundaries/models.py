from django.contrib.gis.db.models import MultiPolygonField
from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel

from unicef_geo.countries.models import Country
from unicef_geo.models import GeoModelMixin


class BoundaryType(TimeStampedModel):
    ZERO = 0
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    ADMIN_LEVEL = (
        (ZERO, 'Level 0'),
        (ONE, 'Level 1'),
        (TWO, 'Level 2'),
        (THREE, 'Level 3'),
        (FOUR, 'Level 4'),
    )

    description = models.CharField(max_length=15)
    admin_level = models.IntegerField(verbose_name=_('Admin Level'), choices=ADMIN_LEVEL)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    is_active = models.BooleanField(verbose_name=_("Active"), default=True)
    is_default = models.BooleanField(default=True, help_text='Default name for country and level')

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        # add check is_default
        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return f'{self.description} {self.get_admin_level_display()} [{self.country}]'


class AdminBoundary(GeoModelMixin):

    COD = 'cod'
    GLOBAL = 'global'

    GENDER = (
        (COD, 'COD'),
        (GLOBAL, 'Global'),
    )

    geom = MultiPolygonField(verbose_name=_("Geometry"), null=True, blank=True, spatial_index=True)
    gender = models.CharField(max_length=15, choices=GENDER)
    # category = models.CharField(max_length=15)
    boundary_type = models.ForeignKey(BoundaryType, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = _('Admin Boundaries')


