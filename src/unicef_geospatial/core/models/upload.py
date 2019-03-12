import fiona
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ValidationError
from django.db import models

from django_fsm import FSMField, transition

from unicef_geospatial.core.models import Country
from unicef_geospatial.core.models.abstracts import FieldMapAbstract


class Upload(models.Model):
    TYPE_COD = 1
    TYPE_GLOBAL = 2
    STATES = ('preparing',
              'ready',
              'queued',
              'in progress',
              'canceled',
              'failed',
              'succeeded')
    state = FSMField(default='preparing',
                     verbose_name='State',
                     choices=list(zip(STATES, STATES)),
                     protected=True,
                     )
    # type_of_upload = models.IntegerField(choices=[(TYPE_COD, 'COD'),
    #                                               (TYPE_GLOBAL, 'Global')])

    country = models.ForeignKey(Country, blank=True, null=True, on_delete=models.CASCADE)
    country_field = models.CharField(max_length=50,
                                     blank=True, null=True,
                                     help_text='If Global set the name of the column that contains Country name')
    date = models.DateTimeField(auto_now_add=True)
    # filename = models.CharField(max_length=255, null=True, blank=True)
    file = models.FileField(null=True, blank=True)
    pattern_filter = models.CharField(max_length=10, default='*')

    boundary_type_policy = models.CharField(max_length=15,
                                            choices=(('get', 'get'),
                                                     ('get_or_create', 'get_or_create'),
                                                     ))
    country_policy = models.CharField(max_length=15,
                                      choices=(('get', 'get'),
                                               ('get_or_create', 'get_or_create'),
                                               ))

    user = models.ForeignKey(User, models.CASCADE, null=True, blank=True)
    metadata = JSONField(null=True, blank=True)
    mapping = JSONField(null=True, blank=True)
    confirm_required = models.BooleanField(default=False,
                                           help_text="Explicitly confirm publication after loading")

    def clean(self):
        if not self.country_field or self.country:
            raise ValidationError('You must set country or country_field')

    @transition(field=state, source='preparing', target='ready')
    def start(self):
        pass

    def _get_shape_field(self, fieldname, props):
        field_map = self.fields.get(geo_field=fieldname)
        if field_map.is_value:
            return field_map.shape_field
        else:
            return props.get(field_map.shape_field)

    def _get_country_by_col(self, props):
        col_value = props[self.country_field]
        return Country.objects.get_by_code(col_value)

    @transition(field=state, source=['preparing', 'ready', 'queued'], target='in progress')
    def process(self):
        if self.country:
            get_country = lambda props: self.country
        else:
            get_country = lambda props: self._get_country_by_col(props)

        with fiona.Env():
            with fiona.open(self.filename) as collection:
                info = {'shapefile': {'meta': collection.meta,
                                      'elements': len(collection)}}

                for key, item in collection.items():
                    props = item['properties']
                    COUNTRY = get_country(props)
                    level = self._get_shape_field('level', props)
                    # TODO: remove me
                    print(111, "upload.py:79", props)
                    print(111, "upload.py:79", level, COUNTRY)

                    # values = {'country': COUNTRY, 'level': self.level}
                    # for field_map in self.fields:
                    #     values[field_map.geo_field] = props[field_map.shape_field]
                    #
                    # if policy == 'get_or_create':
                    #     values['boundary_type'], __ = BoundaryType_policy(admin_level=LEVEL,
                    #                                                       country=COUNTRY,
                    #                                                       defaults={'description': "%s level #%s" % (
                    #                                                           COUNTRY, LEVEL)}
                    #                                                       )
                    # elif policy == 'get':
                    #     values['boundary_type'], __ = BoundaryType_policy(admin_level=LEVEL,
                    #                                                       country=COUNTRY)
                    # else:
                    #     raise ValueError(policy)
                    #
                    # kind = collection.meta['schema']['geometry']
                    # # # If it's type polygon, make it MultiPolygon so it will save to db field
                    # if kind == 'Polygon':
                    #     values['geom'] = GEOSGeometry(json.dumps({
                    #         'type': 'MultiPolygon',
                    #         'coordinates': item['geometry']['coordinates']
                    #     }))
                    # else:
                    #     raise ValueError(kind)
                    # filters = {'country': COUNTRY, 'boundary_type': values['boundary_type'], 'p_code': values['p_code']}
                    # Boundary.timeframes.deactivate(**filters, values=values)

    @transition(field=state, source=['preparing', 'ready', 'queued'], target='canceled')
    def cancel(self):
        pass


class UploadFieldMap(FieldMapAbstract):
    update = models.ForeignKey(Upload, on_delete=models.CASCADE, related_name='fields')
