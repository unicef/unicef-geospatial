import logging

from django.core.management.base import BaseCommand

from unicef_geospatial.core.models import Boundary, BoundaryType, Category, Country, Location

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    args = ''
    help = 'Initalize demo'

    def handle(self, *args, **options):
        public, _ = Category.objects.get_or_create(name="Public")
        school, _ = Category.objects.get_or_create(name="School",
                                                   parent=public)
        hospital, _ = Category.objects.get_or_create(name="Hospital", parent=public)
        ita, _ = Country.objects.get_or_create(name="Italy", iso_code_2='IT', iso_code_3='ITA')
        moz, _ = Country.objects.get_or_create(name="Mozambique", iso_code_2='MO', iso_code_3='MOZ')
        region, _ = BoundaryType.objects.get_or_create(admin_level=BoundaryType.ONE,
                                                       country=ita)
        Boundary.objects.get_or_create(name="Lazio",
                                       country=ita,
                                       gender=Boundary.COD,
                                       boundary_type=region)
        Location.objects.get_or_create(name="Acilia", country=ita)
