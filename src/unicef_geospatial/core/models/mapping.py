from django.contrib.auth.models import User
from django.db import models


class ConfigMap(models.Model):
    name = models.CharField(max_length=255)
    creator = models.ForeignKey(User, models.CASCADE)
    description = models.CharField(max_length=1000, blank=True, null=True)


class FieldMap(models.Model):
    config = models.ForeignKey(ConfigMap, on_delete=models.CASCADE)
    shape_field = models.CharField(max_length=255)
    geo_field = models.CharField(max_length=255)
    mandatory = models.BooleanField(default=True)
