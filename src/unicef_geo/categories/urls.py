from django.conf.urls import include, url

from rest_framework import routers

from .views import CategoryViewSet, SubCategoryViewSet

app_name = 'categories'

api = routers.SimpleRouter()

api.register(r'categories', CategoryViewSet, base_name='category')
api.register(r'subcategories', SubCategoryViewSet, base_name='subcategory')


urlpatterns = [
    url(r'', include(api.urls)),
]
