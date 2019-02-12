import random

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers
from rest_framework.filters import BaseFilterBackend, OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView


def get_random_color():
    return '#%02X%02X%02X' % (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255)
    )


class BaseModelView(ListAPIView):
    filter_backends = (BaseFilterBackend, DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_fields = ('id', 'name')
    ordering_fields = ('name', )

    def get_queryset(self):
        return self.model.objects.all()


def serializer_factory(model, attrs={}, base=serializers.ModelSerializer,
                       fields=None, exclude=None):

    meta_attrs = attrs.copy()
    meta_attrs['model'] = model
    if fields is not None:
        meta_attrs['fields'] = fields
    elif exclude is not None:
        meta_attrs['exclude'] = exclude
    else:
        meta_attrs['fields'] = '__all__'

    parent = (object,)
    if hasattr(base, 'Meta'):
        parent = (base.Meta, object)
    Meta = type(str('Meta'), parent, meta_attrs)

    attrs['Meta'] = Meta
    class_name = model.__name__ + str('Serializer')
    return type(base)(class_name, (base,), attrs)


def lookup_factory(model, base=BaseModelView,
                   serializer=None,
                   fields=None,
                   exclude=None,
                   **kwargs):
    ser_attrs = kwargs.pop('extra_ser_args', {})
    attrs = kwargs.copy()
    attrs['model'] = model

    if fields:
        id, text = fields[:2]
        attrs.setdefault('filter_fields', fields)
    else:
        id, text = ('id', 'name')
        attrs.setdefault('filter_fields', (id, text))

    ttfields = ('id', 'text')
    if exclude:
        ttfields = None

    ser_attrs.update({'id': serializers.CharField(),
                      'text': serializers.CharField(source=text)})

    if serializer is None:
        attrs['serializer_class'] = serializer_factory(model,
                                                       fields=ttfields,
                                                       exclude=exclude,
                                                       attrs=ser_attrs)

    class_name = model.__name__ + str('ListView')
    return type(base)(class_name, (base,), attrs)
