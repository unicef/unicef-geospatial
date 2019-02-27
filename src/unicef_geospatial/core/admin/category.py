from django.contrib.admin import register

from mptt.admin import MPTTModelAdmin

from ..models import Category


@register(Category)
class CategoryAdmin(MPTTModelAdmin):
    search_fields = ('name', 'description')
    list_display = ('name', 'parent', 'description')
