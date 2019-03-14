from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


class FieldMapAbstract(models.Model):
    geo_field = models.CharField(max_length=255)
    shape_field = models.CharField(max_length=255, blank=True, null=True)
    mandatory = models.BooleanField(default=True)
    is_value = models.BooleanField(default=False)

    class Meta:
        abstract = True
        unique_together = ('geo_field', 'shape_field')

    def __str__(self):
        return "%s:%s" % (self.geo_field, self.shape_field)

    def clean(self):
        if not self.shape_field and not self.is_value:
            raise ValidationError(
                "Cannot leave 'shape_field' blank for column mapping. Fill 'shape_field' or set 'is_value' flag.")
