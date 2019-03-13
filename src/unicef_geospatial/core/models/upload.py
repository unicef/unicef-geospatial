import errno
import glob
import json
import os
import shutil
import sys
import tempfile

import fiona
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.functional import cached_property

from django_fsm import FSMField, transition
from pip._vendor.distlib.compat import ZipFile

from unicef_geospatial.core.models import Country, BoundaryType, Boundary
from unicef_geospatial.core.models.abstracts import FieldMapAbstract

IDENTITY_BY_LEVEL = {0: [],
                     1: ['p_code'],
                     2: ['p_code'],
                     3: ['p_code'],
                     4: ['p_code'],
                     }


class Upload(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    file = models.FileField(null=True, blank=True)
    user = models.ForeignKey(User, models.CASCADE, null=True, blank=True)
    metadata = JSONField(null=True, blank=True)

    def __str__(self):
        return self.file.name


class UploadProcessor(models.Model):
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
    upload = models.ForeignKey(Upload, on_delete=models.CASCADE, related_name='processors')
    pattern_filter = models.CharField(max_length=200, default='*')

    remove_files_after_process = models.BooleanField(default=False, blank=True)

    boundary_type_policy = models.CharField(max_length=15,
                                            choices=(('get', 'get'),
                                                     ('get_or_create', 'get_or_create'),
                                                     ))
    country_policy = models.CharField(max_length=15,
                                      choices=(('get', 'get'),
                                               ('get_or_create', 'get_or_create'),
                                               ))

    def __str__(self):
        return self.pattern_filter


    def validate(self):
        for k, v in self.field_map.items():
            if k.startswith('country__'):
                if k[9:] in ['country__%s' % f.name for f in Country._meta.get_fields()]:
                    break
        else:
            return False

    @transition(field=state, source='preparing', target='ready')
    def start(self):
        pass

    @cached_property
    def field_map(self):
        return {r.geo_field: r for r in self.fields.all()}

    def _get_shape_field(self, fieldname):
        field_map = self.field_map[fieldname]
        if field_map.is_value:
            return field_map.shape_field
        else:
            return self.current_record.get(field_map.shape_field)

    def _get_type_by_col(self):
        boundary_type_fields = dict(country=self.current_country, admin_level=self.current_level)
        try:
            return BoundaryType.objects.get(**boundary_type_fields)
        except BoundaryType.DoesNotExist:
            if self.boundary_type_policy == 'get_or_create':
                boundary_type_fields['name'] = '%s #%s' % (self.current_country, self.current_level)
                return BoundaryType.objects.create(**boundary_type_fields)
        except Exception as e:
            # TODO: remove me
            print(111, "upload.py:107", boundary_type_fields)
            print(111, e)
            sys.exit(1)
        raise ValueError('Not enough info to aut create country')

    @property
    def selected_country(self):
        f = self.field_map['country']

        col_value = self.current_record[f.shape_field]
        try:
            return Country.objects.get_by_code(col_value)
        except Country.DoesNotExist:
            if self.country_policy == 'get_or_create':
                country_fields = {}
                for k, v in self.field_map.items():
                    if k.startswith('country__'):
                        country_fields[k[9:]] = self._get_shape_field(k)

                return Country.objects.get_or_create(**country_fields)[0]
        raise ValueError('Not enough info to aut create country')

    @transition(field=state, source=['*'], target='in progress')
    def process(self):
        workdir = None
        objects = []
        try:
            filepath = self.upload.file.path
            if not os.path.isfile(filepath):
                raise Exception('File not found: %s' % filepath)
            with ZipFile(filepath, 'r') as zip_ref:
                workdir = tempfile.mkdtemp(dir=settings.BASE_WORK_DIR)
                zip_ref.extractall(workdir)
                targets = glob.glob(f'{workdir}/{self.pattern_filter}',
                                    recursive=True)
                files = {}
                local_field_names = [f.name for f in Boundary._meta.get_fields()]
                for target in targets:
                    with fiona.Env():
                        with fiona.open(target) as collection:
                            files[target] = {'meta': collection.meta,
                                             'count': len(collection),
                                             'local_field_names': local_field_names,

                                             'records': []}
                            for key, item in collection.items():
                                self.current_record = item['properties']
                                self.current_country = self.selected_country
                                self.current_level = int(self._get_shape_field('level'))
                                self.current_type = self._get_type_by_col()

                                values = {'country': self.current_country,
                                          'boundary_type': self.current_type}

                                for k, v in self.field_map.items():
                                    if k in local_field_names:
                                        values.setdefault(k, self._get_shape_field(k))

                                values['geom'] = GEOSGeometry(json.dumps({
                                    'type': 'MultiPolygon',
                                    'coordinates': item['geometry']['coordinates']
                                }))
                                filters = {'country': self.current_country,
                                           'boundary_type': self.current_type}

                                for k in IDENTITY_BY_LEVEL[self.current_level]:
                                    filters[k] = self._get_shape_field(k)
                                # TODO: remove me
                                print(111, "upload.py:175", values)
                                object = Boundary.timeframes.deactivate(**filters, values=values)
                                objects.append(object)
        except Exception as e:
            raise
        finally:
            if workdir:
                try:
                    shutil.rmtree(workdir)  # delete directory
                except OSError as exc:
                    if exc.errno != errno.ENOENT:  # ENOENT - no such file or directory
                        raise  # re-raise exception
        return objects
                    # with fiona.Env():
        #     with fiona.open(self.filename) as collection:
        #         info = {'shapefile': {'meta': collection.meta,
        #                               'elements': len(collection)}}
        #
        #         for key, item in collection.items():
        #             props = item['properties']
        #             COUNTRY = get_country(props)
        #             level = self._get_shape_field('level', props)
        #             # TODO: remove me
        #             print(111, "upload.py:79", props)
        #             print(111, "upload.py:79", level, COUNTRY)

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
    processor = models.ForeignKey(UploadProcessor,
                               on_delete=models.CASCADE, related_name='fields')

