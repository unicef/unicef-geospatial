import logging

from django.contrib.gis.db import models
from django.utils.translation import ugettext as _

from unicef_geo.categories.models import Category, SubCategory
from unicef_geo.models import GeoModelMixin

logger = logging.getLogger(__name__)


class Location(GeoModelMixin):
    """
    Represents Location, either a point or geospatial object,
    pcode should be unique
    """

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True)
    point = models.PointField(verbose_name=_("Point"), null=True, blank=True)

    def __str__(self):
        return f'{self.name}: {self.p_code})'

    class Meta:
        unique_together = ('name', 'p_code')
