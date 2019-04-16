from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models

from django_fsm import FSMField


class UpdateMetaData(models.Model):
    STATES = ('Queued', 'In Progress', 'Canceled', 'Failed', 'Succeeded')
    state = FSMField(default='Queued',
                     verbose_name='Publication State',
                     choices=list(zip(STATES, STATES)),
                     protected=True,
                     )

    date = models.DateField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE)
    filename = models.CharField(max_length=255)
    metadata = JSONField(null=True, blank=True)
    mapping = JSONField(null=True, blank=True)
    confirm_required = models.BooleanField(help_text="Explicitly confirm publication after loading")
