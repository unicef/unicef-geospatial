import uuid

from django.db import models
from django.utils.translation import ugettext as _

from model_utils.models import TimeStampedModel
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from unicef_geo.countries.models import Country


class AbstractGeoModel(MPTTModel, TimeStampedModel):

    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    ADMIN_LEVEL = (
        (ONE, 'Level 1'),
        (TWO, 'Level 2'),
        (THREE, 'Level 3'),
        (FOUR, 'Level 4'),
    )
    uuid = models.UUIDField(blank=False, editable=False, default=uuid.uuid4, help_text=_('Unique id'))
    name = models.CharField(max_length=127, db_index=True, verbose_name=_('Name'))
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    p_code = models.CharField(verbose_name=_("P Code"), max_length=32, blank=True, null=True)
    admin_level = models.IntegerField(verbose_name=_('Admin Level'), choices=ADMIN_LEVEL)
    parent = TreeForeignKey('self', verbose_name=_("Parent"), null=True, blank=True,
                            related_name='children', on_delete=models.CASCADE)

    is_active = models.BooleanField(verbose_name=_("Active"), default=True, blank=True)

    local_name = models.CharField(max_length=127, verbose_name=_('Local Name'), null=True, blank=True)
    alternate_name_en1 = models.CharField(max_length=127, verbose_name=_('English Name'), null=True, blank=True)
    alternate_name_en2 = models.CharField(max_length=127, verbose_name=_('English Name 2'), null=True, blank=True)
    alternate_name_en3 = models.CharField(max_length=127, verbose_name=_('English Name 3'), null=True, blank=True)
    alternate_name_fr1 = models.CharField(max_length=127, verbose_name=_('French Name'), null=True, blank=True)
    alternate_name_fr2 = models.CharField(max_length=127, verbose_name=_('French Name 2'), null=True, blank=True)
    alternate_name_fr3 = models.CharField(max_length=127, verbose_name=_('French Name 3'), null=True, blank=True)
    alternate_name_es1 = models.CharField(max_length=127, verbose_name=_('Spanish Name'), null=True, blank=True)
    alternate_name_es2 = models.CharField(max_length=127, verbose_name=_('Spanish Name 2'), null=True, blank=True)
    alternate_name_es3 = models.CharField(max_length=127, verbose_name=_('Spanish Name 3'), null=True, blank=True)
    alternate_name_ar1 = models.CharField(max_length=127, verbose_name=_('Arabic Name'), null=True, blank=True)
    alternate_name_ar2 = models.CharField(max_length=127, verbose_name=_('Arabic Name 2'), null=True, blank=True)
    alternate_name_ar3 = models.CharField(max_length=127, verbose_name=_('Arabic Name 3'), null=True, blank=True)

    def __str__(self):
        return f'{self.name} [{self.country}]'

    class Meta:
        abstract = True
