from django.contrib.admin import ModelAdmin, register

from ..models import UpdateMetaData


@register(UpdateMetaData)
class UpdateMetaDataAdmin(ModelAdmin):
    list_display = ('date', 'user',)
