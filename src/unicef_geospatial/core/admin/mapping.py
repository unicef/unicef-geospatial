from django import forms
from django.contrib.admin import ModelAdmin, register, TabularInline

from unicef_geospatial.core.forms import DynamicArrayField

from ..models import ConfigMap, FieldMap


class FieldMapInline(TabularInline):
    model = FieldMap


class MyModelForm(forms.ModelForm):
    class Meta:
        model = ConfigMap
        fields = ['name', 'creator', 'mandatory_fields']
        field_classes = {
            'mandatory_fields': DynamicArrayField,
        }


@register(ConfigMap)
class ConfigMapAdmin(ModelAdmin):
    list_display = ('name', 'creator',)
    inlines = [FieldMapInline]
    form = MyModelForm


@register(FieldMap)
class FieldMapAdmin(ModelAdmin):
    search_fields = ('config', 'shape_field', 'geo_field')
