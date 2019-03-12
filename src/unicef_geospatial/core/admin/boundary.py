from django.contrib.admin import register

from leaflet.admin import LeafletGeoAdmin
from mptt.admin import MPTTModelAdmin

from unicef_geospatial.core.models import BoundaryType

from ..models import Boundary


@register(BoundaryType)
class BoundaryTypeAdmin(LeafletGeoAdmin, MPTTModelAdmin):
    list_display = ('description', 'country', 'parent')
    list_filter = ('country', 'admin_level')


@register(Boundary)
class BoundaryAdmin(LeafletGeoAdmin, MPTTModelAdmin):
    search_fields = ('name', 'p_code', 'iso_code_3')
    list_display = ('name', 'country', 'p_code', 'active', 'boundary_type')
    list_filter = ('country', 'active', 'boundary_type__level')
    date_hierarchy = 'valid_from'
