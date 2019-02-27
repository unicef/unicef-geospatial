from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import ugettext_lazy as _


class NamesMixin(models.Model):
    name_en = models.CharField(max_length=127, verbose_name=_('English Name'), null=True, blank=True)
    name_fr = models.CharField(max_length=127, verbose_name=_('French Name'), null=True, blank=True)
    name_es = models.CharField(max_length=127, verbose_name=_('Spanish Name'), null=True, blank=True)
    name_ar = models.CharField(max_length=127, verbose_name=_('Arabic Name'), null=True, blank=True)
    alternate_names = JSONField(null=True, blank=True)

    class Meta:
        abstract = True
