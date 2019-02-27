import uuid as uuid

from django.db import models
from django.utils.translation import ugettext_lazy as _

from model_utils.models import TimeStampedModel


class BaseGeoModel(TimeStampedModel):
    uuid = models.UUIDField(blank=False, editable=False, default=uuid.uuid4, help_text=_('Unique id'))

    class Meta:
        abstract = True
