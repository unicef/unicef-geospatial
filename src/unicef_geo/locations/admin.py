from django.contrib.admin import register

from leaflet.admin import LeafletGeoAdmin
from mptt.admin import MPTTModelAdmin

from .models import Location


@register(Location)
class LocationAdmin(LeafletGeoAdmin, MPTTModelAdmin):
    fields = [
        'name',
        'country',
        'p_code',
        'point',
    ]
    list_display = (
        'name',
        'country',
        'p_code',
        'is_active',
    )
    list_filter = (
        'parent',
    )
    search_fields = ('name', 'p_code',)
