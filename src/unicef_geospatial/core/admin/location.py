from django.contrib.admin import register

from leaflet.admin import LeafletGeoAdmin
from mptt.admin import TreeRelatedFieldListFilter

from ..models import Location


@register(Location)
class LocationAdmin(LeafletGeoAdmin):
    # fields = ['name', 'country', 'p_code', 'point', ]
    list_display = ('name', 'country', 'p_code', 'is_active',)
    search_fields = ('name', 'p_code',)

    list_filter = (
        ('category', TreeRelatedFieldListFilter),
    )
    # def get_form(self, request, obj=None, **kwargs):
    #     widget = JSONEditorWidget(dynamic_schema, False)
    #     form = super().get_form(request, obj, widgets={'tags': widget}, **kwargs)
    #     return form
