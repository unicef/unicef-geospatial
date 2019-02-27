from django.db import models
from django.utils.translation import ugettext_lazy as _

from model_utils.models import TimeStampedModel
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel


class Category(MPTTModel, TimeStampedModel):
    name = models.CharField(max_length=64, unique=True, verbose_name=_('Name'))
    description = models.CharField(max_length=512, verbose_name=_('Description'), null=True, blank=True)
    parent = TreeForeignKey('self', verbose_name=_("Parent"), null=True, blank=True,
                            related_name='subcategories', on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name
