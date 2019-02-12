from rest_framework.viewsets import ReadOnlyModelViewSet
from unicef_geo.libs import serializer_factory

from .models import Category, SubCategory


class CategoryViewSet(ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = serializer_factory(Category)


class SubCategoryViewSet(ReadOnlyModelViewSet):
    queryset = SubCategory.objects.all()
    serializer_class = serializer_factory(SubCategory)
