from django.contrib.contenttypes.models import ContentType
from django.db import models

from unicef_geospatial.core.models import Boundary, Country, Location
from unicef_geospatial.state.fields import CreatorUserField, ModifierUserField

TARGETS = [m._meta.model_name for m in (Country, Location, Boundary)]


class ConfigMap(models.Model):
    name = models.CharField(max_length=255)
    creator = CreatorUserField()
    modifier = ModifierUserField()
    description = models.CharField(max_length=1000, blank=True, null=True)
    target = models.ForeignKey(ContentType,
                               on_delete=models.CASCADE,
                               limit_choices_to={'model__in': TARGETS,
                                                 'app_label': 'core'})


class FieldMap(models.Model):
    config = models.ForeignKey(ConfigMap, on_delete=models.CASCADE)
    geo_field = models.CharField(max_length=255)
    shape_field = models.CharField(max_length=255)
    mandatory = models.BooleanField(default=True)
