
from django.db import models
from django.utils.translation import ugettext_lazy as _

from unicef_geospatial.core.models.base import BaseGeoModel
from unicef_geospatial.core.models.mixins import GeoModel

CONTINENTS = (
    ('AF', _('Africa')),
    ('AN', _('Antartica')),
    ('AS', _('Asia')),
    ('EU', _('Europe')),
    ('NA', _('North America')),
    ('OC', _('Oceania')),
    ('SA', _('South America')),
)


class Country(GeoModel, BaseGeoModel):
    name = models.CharField(max_length=127, db_index=True, verbose_name=_('Name'))
    fullname = models.CharField(max_length=127, db_index=True, verbose_name=_('Full Name'), null=True, blank=True)
    alternate_name = models.CharField(max_length=127, db_index=True, verbose_name=_('Alternate Name'),
                                      null=True, blank=True)

    iso_code_2 = models.CharField(max_length=2, unique=True, verbose_name=_('ISO code 2'))
    iso_code_3 = models.CharField(max_length=3, unique=True, verbose_name=_('ISO code 3'))
    un_number = models.CharField(max_length=3, verbose_name=_('UN Number'), null=True, blank=True)

    continent = models.CharField(choices=CONTINENTS, max_length=2)

    class Meta:
        verbose_name_plural = _('Countries')

    def __str__(self):
        return self.name
