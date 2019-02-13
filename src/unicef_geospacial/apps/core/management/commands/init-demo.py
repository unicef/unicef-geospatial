# -*- coding: utf-8 -*-
import logging

from django.core.management.base import BaseCommand

from unicef_geo.boundaries.models import AdminBoundary
from unicef_geo.categories.models import Category, SubCategory
from unicef_geo.countries.models import Country
from unicef_geo.locations.models import Location

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    args = ''
    help = 'Initalize demo'

    def handle(self, *args, **options):
        public, _ = Category.objects.get_or_create(name="Public")
        school, _ = SubCategory.objects.get_or_create(name="School", category=public)
        hospital, _ = SubCategory.objects.get_or_create(name="Hospital", category=public)
        ita, _ = Country.objects.get_or_create(name="Italy", iso_code_2='IT', iso_code_3='ITA')
        AdminBoundary.objects.get_or_create(name="Lazio", country=ita, admin_level=AdminBoundary.ONE,
                                            gender=AdminBoundary.COD)
        Location.objects.get_or_create(name="Acilia", country=ita, admin_level=AdminBoundary.THREE)
