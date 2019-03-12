from django.contrib.gis.db.models import MultiPolygonField, Q
from django.db import models
from django.utils.translation import ugettext_lazy as _

from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from .base import BaseGeoModel
from .country import Country
from .mixins import GeoModel, NamesMixin, TimeFramedMixin


class BoundaryType(GeoModel, MPTTModel, BaseGeoModel):
    ZERO = 0
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    ADMIN_LEVEL = (
        (ZERO, 'Level 0'),
        (ONE, 'Level 1'),
        (TWO, 'Level 2'),
        (THREE, 'Level 3'),
        (FOUR, 'Level 4'),
        (FIVE, 'Level 5'),
    )

    description = models.CharField(max_length=250)
    admin_level = models.IntegerField(verbose_name=_('Admin Level'), choices=ADMIN_LEVEL)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    parent = TreeForeignKey('self', verbose_name=_("Parent"), null=True, blank=True,
                            related_name='children', on_delete=models.CASCADE)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        # add check is_default
        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return f'{self.description} {self.get_admin_level_display()} [{self.country}]'


class Boundary(GeoModel, NamesMixin, MPTTModel, BaseGeoModel):
    COD = 'cod'
    GLOBAL = 'global'

    GENDER = (
        (COD, 'COD'),
        (GLOBAL, 'Global'),
    )

    geom = MultiPolygonField(verbose_name=_("Geometry"), null=True, blank=True, spatial_index=True)
    gender = models.CharField(max_length=15, choices=GENDER)
    boundary_type = models.ForeignKey(BoundaryType, on_delete=models.CASCADE)
    name = models.CharField(max_length=127, db_index=True, verbose_name=_('Name'))
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    p_code = models.CharField(verbose_name=_("P Code"), max_length=32, blank=True, null=True)
    parent = TreeForeignKey('self', verbose_name=_("Parent"), null=True, blank=True,
                            related_name='children', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.name} [{self.country}]'

    class Meta:
        verbose_name_plural = _('Admin Boundaries')
        constraints = [models.UniqueConstraint(fields=['p_code', 'country', 'level', 'active'],
                                               name='unique_active_pcode',
                                               condition=Q(active=True)),
                       ]

    def clean(self):
        # check that boundary_type and parent belong same country
        super().clean()
