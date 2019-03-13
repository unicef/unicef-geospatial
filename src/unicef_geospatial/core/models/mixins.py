from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models import QuerySet
from django.utils import timezone
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


class TimeFramedQuerySet(QuerySet):
    def deactivate(self, **kwargs):
        expired = kwargs.pop('expired', timezone.now())
        values = kwargs.pop('values')
        values['active'] = True
        values['valid_to'] = None
        values['valid_from'] = timezone.now()
        filters = dict(kwargs)
        # TODO: remove me
        print(111, "mixins.py:29", 9999, "filters:", filters)
        print(111, "mixins.py:29", 9999, "values:", values)
        aaa = self.filter(**filters).update(active=False, valid_to=expired)

        # TODO: remove me
        print(111, "mixins.py:33", aaa)
        return self.create(**values)


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
    active = models.BooleanField(verbose_name=_("Active"), default=True, null=True, blank=True)

    objects = models.Manager()
    timeframes = TimeFramedQuerySet.as_manager()

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
