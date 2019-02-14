from django.contrib.admin import register

from leaflet.admin import LeafletGeoAdmin
from mptt.admin import MPTTModelAdmin

from .models import AdminBoundary


@register(AdminBoundary)
class AdminBoundaryAdmin(LeafletGeoAdmin, MPTTModelAdmin):
    search_fields = ('name', 'p_code', 'iso_code_3')
    list_display = ('name', 'country', 'p_code', 'gender')
    list_filter = ('country', )
