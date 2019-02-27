from django.contrib.admin import ModelAdmin, register

from ..models import Country


@register(Country)
class CountryAdmin(ModelAdmin):
    search_fields = ('name', 'fullname', 'iso_code_2', 'iso_code_3')
    list_display = ('name', 'fullname', 'iso_code_2', 'iso_code_3', 'continent')
    list_filter = ('continent', )
