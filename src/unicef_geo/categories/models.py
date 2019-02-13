from django.db import models
from django.utils.translation import ugettext_lazy as _

from model_utils.models import TimeStampedModel


class Category(TimeStampedModel):
    name = models.CharField(max_length=64, unique=True, verbose_name=_('Name'))
    description = models.CharField(max_length=512, verbose_name=_('Description'), null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class SubCategory(TimeStampedModel):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=64, unique=True, verbose_name=_('Name'))
    description = models.CharField(max_length=512, verbose_name=_('Description'), null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Subcategories'

    def __str__(self):
        return self.name
