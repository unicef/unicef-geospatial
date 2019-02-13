from django.contrib.admin import ModelAdmin, register

from .models import Category, SubCategory


@register(Category)
class CategoryAdmin(ModelAdmin):
    search_fields = ('name', 'description')
    list_display = ('name', 'description')


@register(SubCategory)
class SubCategoryAdmin(ModelAdmin):
    search_fields = ('name', 'description')
    list_display = ('name', 'description')
    list_filter = ('category', )
