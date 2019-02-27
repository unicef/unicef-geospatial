from django.contrib.gis.db.models import PointField
from django.db import models
from django.utils.translation import ugettext as _

from .base import BaseGeoModel
from .category import Category
from .country import Country
from .mixins import NamesMixin


class Location(NamesMixin, BaseGeoModel):
    name = models.CharField(max_length=127, db_index=True, verbose_name=_('Name'))
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    p_code = models.CharField(verbose_name=_("P Code"), max_length=32, blank=True, null=True)
    point = PointField(verbose_name=_("Point"), null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(verbose_name=_("Active"), default=True, blank=True)

    def __str__(self):
        return f'{self.name} [{self.country}]'
