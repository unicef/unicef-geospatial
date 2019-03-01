import json
import os

from django.contrib.gis.geos import GEOSGeometry
from django.core.management.base import BaseCommand

import fiona

from unicef_geospatial.core.models import Boundary, BoundaryType, Country


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('shapefileSet', nargs='+', type=str)

    def handle(self, *args, **options):
        # In the repository, ./public/gadm3-6/ has a single country folder: AFG
        # However, when running in production, ./public will be mounted with file storage
        # that contains all countries.
        shapefile_set = options['shapefileSet'][0]
        countries = os.listdir(f'./public/{shapefile_set}/')
        for iso3 in countries:
            files = os.listdir(f'./public/{shapefile_set}/{iso3}')
            # Filter only .shp files
            shapefiles = list(filter(lambda name: '.shp' in name, files))
            for shapefile in shapefiles:
                tmp = shapefile.split('.shp')
                adminLevel = tmp[0][-1:]
                # Open shapefile
                shps = fiona.open(f'./public/{shapefile_set}/{iso3}/{shapefile}')
                for shp in shps:
                    country, _ = Country.objects.get_or_create(
                        name=shp.get('properties').get('NAME_0'),
                        iso_code_3=iso3
                    )
                    boundary_type, _ = BoundaryType.objects.get_or_create(
                        admin_level=adminLevel,
                        country=country
                    )
                    # kind will be either Polygon or MultiPolygon
                    kind = shp.get('geometry').get('type')
                    # If it's type polygon, make it MultiPolygon so it will save to db field
                    if kind == 'Polygon':
                        mpolygon = {
                            'type': 'MultiPolygon',
                            'coordinates': shp.get('geometry').get('coordinates')
                        }
                        place_name = shp.get('properties').get(f'NAME_{adminLevel}')
                        print(f'Saving {iso3} {adminLevel} {place_name}')
                        Boundary.objects.get_or_create(
                            name=place_name,
                            country=country,
                            gender=Boundary.GLOBAL,
                            boundary_type=boundary_type,
                            geom=GEOSGeometry(json.dumps(mpolygon))
                        )
