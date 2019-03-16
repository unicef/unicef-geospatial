import errno
import glob
import json
import logging
import os
import shutil
import sys
import tempfile

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon
from django.contrib.postgres.fields import JSONField
from django.db import models, transaction
from django.utils.functional import cached_property

import fiona
from django_fsm import FSMField, transition
from pip._vendor.distlib.compat import ZipFile

from unicef_geospatial.core.models import Boundary, BoundaryType, Country
from unicef_geospatial.core.models.abstracts import FieldMapAbstract

IDENTITY_BY_LEVEL = {0: [],
                     1: ['p_code'],
                     2: ['p_code'],
                     3: ['p_code'],
                     4: ['p_code'],
                     }

logger = logging.getLogger(__name__)


def sane_repr(iterable):
    return ",".join(["'%s'" % e for e in iterable])


class FieldMap:
    def __init__(self, queryset):
        self._data = {r.geo_field: r for r in queryset.all()}

    def __getattr__(self, name):
        return self._data[name]

    def items(self):
        return self._data.items()

    def __getitem__(self, name):
        try:
            return self._data[name]
        except KeyError:
            raise ValueError("""FieldMap does not contains field '%s'. It contains %s.
""" % (name, sane_repr(self._data.keys())))


class GetAttrWrapper:
    def __init__(self, feature_properties):
        self._feature_properties = feature_properties

    def __getattr__(self, item):
        return self._feature_properties[item]


class MappedGetAttrWrapper:
    def __init__(self, feature_properties, mapping):
        self._feature_properties = feature_properties
        self.cols = feature_properties.keys()
        self._mapping = mapping

    def __getattr__(self, geo_field):
        fieldmap = self._mapping[geo_field]
        if fieldmap.is_value:
            return fieldmap.shape_field
        try:
            return self._feature_properties[fieldmap.shape_field]
        except KeyError:
            raise ValueError("""Cannot find column '%s' in feature. It contains %s.
Maybe field '%s' FieldMap should have 'is_value' set ? 
""" % (fieldmap.shape_field, sane_repr(self.cols), geo_field))


class ShapeRowHandler:
    def __init__(self, processor, feature):
        self.processor = processor
        # self.row = feature
        # self.raw = GetAttrWrapper(feature['properties'])
        self.values = MappedGetAttrWrapper(feature['properties'], processor.field_map)
        # self.map = MappedGetAttrWrapper(row['properties'], processor.field_map)

    # country, level, boundary_type and parent are special columns

    @cached_property
    def level(self):
        return int(self.values.level)

    @cached_property
    def parent(self):
        if self.level == 0:
            return None
        else:
            filters = {'country': self.country,
                       'p_code': self.values.parent,
                       'boundary_type__level': self.level - 1,
                       'active': True}
            try:
                return Boundary.objects.get(**filters)
            except Boundary.DoesNotExist:
                raise Exception("""Unable to find parent for %s using %s""" % ("", str(filters)))

    @cached_property
    def boundary_type(self):
        # target = self.values.boundary_type
        try:
            ret = BoundaryType.objects.get(country=self.country,
                                           active=True,
                                           admin_level=self.level)
        except BoundaryType.DoesNotExist:
            if self.processor.boundary_type_policy == 'get_or_create':
                parent = BoundaryType.objects.get(country=self.country,
                                                  active=True,
                                                  admin_level=self.level - 1)
                ret = BoundaryType.objects.create(country=self.country,
                                                  active=True,
                                                  parent=parent,
                                                  admin_level=self.level,
                                                  name=self.values.boundary_type__name)
            else:
                self.processor.logger.debug("Unable to find BoundaryType '%s'" % target)
                raise
        self.processor.logger.debug('BoundaryType set to %s' % ret)
        return ret

    @cached_property
    def country(self):
        target = self.values.country
        try:
            ret = Country.objects.get_by_code(target)
        except Country.DoesNotExist:
            if self.processor.country_policy == 'get_or_create':
                ret = Country.objects.create(name=self.values.country__name,
                                             iso_code_2=self.values.country__iso_code_2,
                                             iso_code_3=self.values.country__iso_code_3,
                                             )
            else:
                self.processor.logger.debug("Unable to find country '%s'" % target)
                raise
        self.processor.logger.debug('Country set to %s' % ret)
        return ret

    def __repr__(self):
        return "%s - %s" % (self.row.keys(), self.row['properties'].keys())


class Upload(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    file = models.FileField(null=True, blank=True)
    user = models.ForeignKey(User, models.CASCADE, null=True, blank=True)
    metadata = JSONField(null=True, blank=True)

    def __str__(self):
        return "#%d %s" % (self.id, self.file.name)


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
                     protected=False,
                     )

    upload = models.ForeignKey(Upload, on_delete=models.CASCADE,
                               related_name='processors')
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

    logger = logger

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
        return FieldMap(self.fields)

    @transition(field=state, source=['*'], target='in progress')
    def process(self):
        workdir = None
        objects = []
        with transaction.atomic():
            try:
                filepath = self.upload.file.path
                if not os.path.isfile(filepath):
                    raise Exception('Error processing %s. File not found: %s' % (self, filepath))

                with ZipFile(filepath, 'r') as zip_ref:
                    self.logger.info('Processing %s' % filepath)
                    workdir = tempfile.mkdtemp(dir=settings.BASE_WORK_DIR)
                    zip_ref.extractall(workdir)
                    self.logger.debug('Unzipping %s to %s' % (filepath, workdir))
                    targets = glob.glob(f'{workdir}/{self.pattern_filter}', recursive=True)
                    files = {}
                    local_field_names = [f.name for f in Boundary._meta.get_fields()]
                    for target in targets:
                        self.logger.debug('Processing %s' % target)
                        with fiona.Env():
                            with fiona.open(target) as collection:
                                files[target] = {'meta': collection.meta,
                                                 'count': len(collection),
                                                 'local_field_names': local_field_names,
                                                 'records': []}
                                for key, item in collection.items():
                                    self.current_record = ShapeRowHandler(self, item)
                                    filters = {'country': self.current_record.country,
                                               'boundary_type': self.current_record.boundary_type,
                                               'p_code': self.current_record.values.p_code
                                               }

                                    values = {'country': self.current_record.country,
                                              'boundary_type': self.current_record.boundary_type,
                                              'p_code': self.current_record.values.p_code,
                                              'parent': self.current_record.parent,
                                              }
                                    for k, v in self.field_map.items():
                                        if k in local_field_names:
                                            values.setdefault(k, getattr(self.current_record.values, k))

                                    gtype = item['geometry']['type']
                                    if gtype == 'Polygon':
                                        values['geom'] = GEOSGeometry(json.dumps({
                                            'type': 'MultiPolygon',
                                            'coordinates': item['geometry']['coordinates']
                                        }))
                                    else:
                                        self.logger.error("Geometry type '%s' not supported" % gtype)
                                        # raise NotImplementedError("Geometry type '%s' not supported" % gtype)

                                    self.logger.debug("Deactivating %s" % repr(filters))
                                    self.logger.debug("Adding/Updating %s" % repr(values))
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

    @transition(field=state, source=['preparing', 'ready', 'queued'], target='canceled')
    def cancel(self):
        pass


class UploadFieldMap(FieldMapAbstract):
    processor = models.ForeignKey(UploadProcessor,
                                  on_delete=models.CASCADE, related_name='fields')

    class Meta:
        unique_together = ('processor', 'geo_field', 'shape_field')
