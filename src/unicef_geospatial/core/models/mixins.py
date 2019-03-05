from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import ugettext_lazy as _

from django_fsm import FSMField, transition


class NamesMixin(models.Model):
    name_en = models.CharField(max_length=127, verbose_name=_('English Name'), null=True, blank=True)
    name_fr = models.CharField(max_length=127, verbose_name=_('French Name'), null=True, blank=True)
    name_es = models.CharField(max_length=127, verbose_name=_('Spanish Name'), null=True, blank=True)
    name_ar = models.CharField(max_length=127, verbose_name=_('Arabic Name'), null=True, blank=True)
    alternate_names = JSONField(null=True, blank=True)

    class Meta:
        abstract = True


class TimeFramedMixin(models.Model):
    valid_from = models.DateTimeField(_('start'), null=True, blank=True)
    valid_to = models.DateTimeField(_('end'), null=True, blank=True)

    class Meta:
        abstract = True


class GeoModel(TimeFramedMixin):
    STATES = ('Pending Approval', 'Active', 'Archived')

    state = FSMField(default='Active',
                     verbose_name='Record State',
                     choices=list(zip(STATES, STATES)),
                     protected=True,
                     )
    # TODO: redundant for performace, but needs investigations
    active = models.BooleanField(verbose_name=_("Active"), default=True)

    class Meta:
        abstract = True

    @transition(field=state, source='*', target='Active')
    def activate(self):
        pass

    @transition(field=state, source='Pending Approval', target='Active')
    def approve(self):
        pass

    @transition(field=state, source='Active', target='Archived')
    def archive(self):
        pass
