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


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('args', nargs='*')

    def handle(self, *args, **options):
        if not args:
            for u in Upload.objects.all():
                self.stdout.write("%003s %a" % (u.pk, u.file.name))
            return ""

        for pk in args:
            target = Upload.objects.get(id=pk)
            for processor in target.processors.all():
                objects = processor.process()
                self.stdout.write(str(objects))
