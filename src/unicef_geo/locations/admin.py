from django.contrib.admin import register

from leaflet.admin import LeafletGeoAdmin
from mptt.admin import MPTTModelAdmin

from .models import Location


@register(Location)
class LocationAdmin(LeafletGeoAdmin, MPTTModelAdmin):
    fields = [
        'name',
        'country',
        'admin_level',
        'p_code',
        'point',
    ]
    list_display = (
        'name',
        'country',
        'admin_level',
        'p_code',
        'is_active',
    )
    list_filter = (
        'admin_level',
        'parent',
    )
    search_fields = ('name', 'p_code',)
