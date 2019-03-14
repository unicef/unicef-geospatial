# This is a first draft of a task to bootstrap the project with
# admin boundaries from GADM
import glob
import json
import logging
import os
import re
from functools import partial
from pathlib import Path

from django.contrib.gis.geos import GEOSGeometry
from django.core.management.base import BaseCommand, CommandError

import fiona

from unicef_geospatial.core.models import Boundary, BoundaryType, Country, Upload


def getLogger():
    logger = logging.getLogger('spam_application')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('args', nargs='*')
        parser.add_argument('--debug', action='store_true')

    def handle(self, *args, **options):
        logger = getLogger()

        if not args:
            for u in Upload.objects.all():
                self.stdout.write("%003s %a" % (u.pk, u.file.name))
            return ""

        for pk in args:
            if '.' in pk:
                pk, pk1 = pk.split('.')
                sub = {'pk': pk1}
            else:
                sub = {}

            target = Upload.objects.get(id=pk)
            logger.info('Processing %s' % target)
            try:
                for processor in target.processors.order_by('id').filter(**sub):
                    processor.logger = logger

                    objects = processor.process()
                    self.stdout.write(str(objects))
            except Exception as e:
                logger.error(e)
                if options['debug']:
                    raise
                return ""
