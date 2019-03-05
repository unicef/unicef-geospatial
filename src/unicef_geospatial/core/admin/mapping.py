from django.contrib.admin import ModelAdmin, register, TabularInline

from ..models import ConfigMap, FieldMap


class FieldMapInline(TabularInline):
    model = FieldMap
    fields = ('geo_field', 'shape_field', 'mandatory')


@register(ConfigMap)
class ConfigMapAdmin(ModelAdmin):
    list_display = ('name', 'creator', 'target')
    inlines = [FieldMapInline]
    list_filter = ('target',)


@register(FieldMap)
class FieldMapAdmin(ModelAdmin):
    search_fields = ('config', 'shape_field', 'geo_field')
