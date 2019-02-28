import shapefile
import fiona
import os
import re
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon
from unicef_geo.boundaries.models import AdminBoundary, BoundaryType
from unicef_geo.categories.models import Category, SubCategory
from unicef_geo.countries.models import Country
from unicef_geo.locations.models import Location
import json

class Command(BaseCommand):
    def handle(self, *args, **options):
        # In the repository, ./public/gadm3-6/ has a single country folder: AFG
        # However, when running in production, ./public will be mounted with file storage
        # that contains all countries.
        set = 'gadm3-6'
        countries = os.listdir(f"./public/{set}/")
        for iso3 in countries:
            files = os.listdir(f"./public/{set}/{iso3}")
            # Filter only .shp files
            shapefiles = list(filter(lambda name: '.shp' in name, files))
            for shapefile in shapefiles:
                tmp = shapefile.split(".shp")
                adminLevel = tmp[0][-1:]
                # Open shapefile
                shps = fiona.open(f'./public/{set}/{iso3}/{shapefile}')
                for shp in shps:
                    # Create ita
                    ita, _ = Country.objects.get_or_create(
                    name=shp.get('properties').get('NAME_0'),
                    iso_code_3=iso3
                    )
                    # Create region
                    region, _ = BoundaryType.objects.get_or_create(
                    admin_level=adminLevel,
                    country=ita
                    )
                    # kind will be either Polygon or MultiPolygon
                    kind = shp.get('geometry').get('type')
                    mpolygon= shp.get('geometry')
                    # If it's type polygon, make it MultiPolygon so it will save to db field
                    if kind == 'Polygon':
                        mpolygon = {}
                        mpolygon['type'] = 'MultiPolygon'
                        mpolygon['coordinates'] = [shp.get('geometry').get('coordinates')]
                        placeName = name=shp.get('properties').get(f'NAME_{adminLevel}')
                        print(f"Saving {iso3} {adminLevel} {placeName}")
                        AdminBoundary.objects.get_or_create(
                        name=placeName,
                        country=ita,
                        gender=AdminBoundary.GLOBAL,
                        boundary_type=region,
                        geom=GEOSGeometry(json.dumps(mpolygon))
                        )
