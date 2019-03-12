# This is a first draft of a task to bootstrap the project with
# admin boundaries from GADM
import glob
import json
import os
import re
from functools import partial
from pathlib import Path

from django.contrib.gis.geos import GEOSGeometry
from django.core.management.base import BaseCommand, CommandError

import fiona

from unicef_geospatial.core.models import Boundary, BoundaryType, Country, Upload


def get_level_resolver(config):
    if config.get('level') is None:
        if 'level' not in config['fields']:
            raise ValueError('fields mapping must contains "level" mapping')
        get_level = lambda props: int(props[config['fields']['level']])
    else:
        get_level = lambda props: int(config.get('level'))
    return get_level


def get_country_resolver(config):
    if config.get('country'):
        try:
            filters = {'un_number': int(config['country'])}
        except ValueError:
            if len(config['country']) == 2:
                filters = {'iso_code_2': config['country']}
            elif len(config['country']) == 3:
                filters = {'iso_code_3': config['country']}
            else:
                raise ValueError('Invalid country code %s' % config['country'])
        try:
            get_country = lambda props: Country.objects.get(**filters)
        except (Country.DoesNotExist, Country.MultipleObjectsReturned):
            raise ValueError('Invalid country code %s' % config['country'])
    else:  # config['country_field']:
        get_country = lambda props: props.get(config['country_field'])

    return get_country


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('folder', type=str)
        parser.add_argument('--country', type=str)
        parser.add_argument('--country-field', dest='country_field', type=str)
        parser.add_argument('--filter', default='*', type=str)
        parser.add_argument('--mapping', default="", type=str)
        parser.add_argument('--fixed', default="", type=str)
        #
        parser.add_argument('--country-policy', dest='country_policy',
                            default='get_or_create', type=str)
        parser.add_argument('--type-policy', dest='boundary_type_policy',
                            default='get_or_create', type=str)


    def handle(self, folder, *args, **options):
        if not os.path.isdir(folder):
            raise CommandError('"%s" does not seem a valid directory' % folder)
        path = Path(folder)
        shapefiles = path.glob('%s.shp' % options['filter'])
        if not shapefiles:
            raise ValueError('"%s" does not contains any *.shp file' % path)

        fields = ['country', 'country_field',
                  'filename', 'country_policy', 'boundary_type_policy',
                  ]

        mapping = {k.split('=')[0]: k.split('=')[1] for k in options.pop('mapping').split(',')}
        fixed = {k.split('=')[0]: k.split('=')[1] for k in options.pop('fixed').split(',')}
        values = {k: v for k, v in options.items() if k in fields}
        if options.get('country'):
            values['country'] = Country.objects.get_by_code(options['countr'])
        #     try:
        #         filters = {'un_number': int(options['country'])}
        #     except ValueError:
        #         if len(options['country']) == 2:
        #             filters = {'iso_code_2': options['country']}
        #         elif len(options['country']) == 3:
        #             filters = {'iso_code_3': options['country']}
        #         else:
        #             raise ValueError('Invalid country code %s' % options['country'])
        #     try:
        #         values['country'] = Country.objects.get(**filters)
        #     except (Country.DoesNotExist, Country.MultipleObjectsReturned):
        #         raise ValueError('Invalid country code %s' % options['country'])

        for shapefile in shapefiles:
            values['filename'] = shapefile
            u = Upload(**values)
            u.clean()
            u.save()
            for k, v in mapping.items():
                u.fields.create(geo_field=k,
                                shape_field=v,
                                is_value=False)

            for k, v in fixed.items():
                u.fields.create(geo_field=k,
                                shape_field=v,
                                is_value=True)

            u.process()

        #
        # config = {'country': options['country'],
        #           'country_field': options['country_field'],
        #           'level': options['level'],
        #           'fields': {'level': options['level'],
        #                      'name': options['name'],
        #                      'p_code': options['code']
        #                      }
        #           }
        #
        # try:
        #     load(folder, config, filter=options['filter'],
        #          )
        # except Exception as e:
        #     raise CommandError(e)
