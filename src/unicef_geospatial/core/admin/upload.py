import glob
import os
from zipfile import ZipFile

import fiona
from admin_extra_urls.extras import ExtraUrlMixin, link, action
from django import forms
from django.contrib.admin import ModelAdmin, register, TabularInline
from django.template.response import TemplateResponse

from unicef_geospatial.core.forms.upload import UploadCreateForm
from unicef_geospatial.core.forms.upload_wizard import UploadWizardView
from ..models import Upload, UploadFieldMap


class FieldMapInline(TabularInline):
    model = UploadFieldMap
    fields = ('geo_field', 'shape_field', 'mandatory')


@register(Upload)
class UploadAdmin(ExtraUrlMixin, ModelAdmin):
    list_display = ('date', 'user', 'file', 'country')
    # add_form_template = None
    # change_form_template = None
    form = forms.ModelForm
    add_form = UploadCreateForm
    inlines = [FieldMapInline]
    readonly_fields = ('state', 'user')
    exclude = ('metadata', 'mapping')

    #
    # def get_form(self, request, obj=None, change=False, **kwargs):
    #     if not obj:
    #         self.form = self.add_form
    #     return super().get_form(request, obj, change, **kwargs)

    def get_context_for_object(self, **kwargs):
        opts = self.object._meta
        ctx = {"opts": opts,
               "original": self.object,
               "app_label": opts.app_label,
               "has_view_permission": True,
               }
        ctx.update(**kwargs)
        return ctx

    @action()
    def inspect_zip(self, request, pk):
        self.object = Upload.objects.get(pk=pk)

        with ZipFile(self.object.file, 'r') as myzip:
            files = sorted(filter(lambda x: not x.startswith('__MACOSX'), myzip.namelist()))

        return TemplateResponse(request,
                                'admin/zipfile.html', self.get_context_for_object(files=files))

    @action()
    def inspect_shape(self, request, pk):
        self.object = Upload.objects.get(pk=pk)

        with ZipFile(self.object.file, 'r') as zip_ref:
            workdir = "/data/PROGETTI/UNICEF/unicef-geospatial/~build/aaaa"
            zip_ref.extractall(workdir)
            targets = glob.glob(f'{workdir}/**/{self.object.pattern_filter}.shp',
                                recursive=True)
            files = {}
            for target in targets:
                with fiona.Env():
                    with fiona.open(target) as collection:
                        files[target] = {'meta': collection.meta,
                                         'count': len(collection)}
                        item = next(collection.items())
                        if item:
                            item = item[1]
                            item['geometry']['coordinates'] = '...trucated...'
                            files[target]['sample'] = item

        return TemplateResponse(request, 'admin/shapefile.html',
                                self.get_context_for_object(files=files))

    @action()
    def process(self, request, pk):
        meta = Upload.objects.get(pk=pk)
        meta.process()

    @link()
    def wizard(self, request):
        opts = self.model._meta
        view = UploadWizardView.as_view(opts=opts, modeladmin=self)
        return view(request)
        # context = {'form': }
        # return TemplateResponse(request, "admin/upload_wizard.html", context)


class UploadFieldMapAdmin(ModelAdmin):
    search_fields = ('config', 'shape_field', 'geo_field')
