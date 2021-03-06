import errno
import glob
import os
import shutil
import tempfile
from zipfile import ZipFile

from django import forms
from django.conf import settings
from django.contrib.admin import ModelAdmin, register, TabularInline
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse

import fiona
from admin_extra_urls.extras import action, ExtraUrlMixin

from unicef_geospatial.core.forms.upload import UploadFieldMapForm
from unicef_geospatial.core.views import Process

from ..models import Upload, UploadFieldMap, UploadProcessor


class FieldMapInline(TabularInline):
    model = UploadFieldMap
    form = UploadFieldMapForm
    fields = ('geo_field', 'shape_field', 'mandatory', 'is_value')


class ProcessorInline(TabularInline):
    model = UploadProcessor


@register(Upload)
class UploadAdmin(ExtraUrlMixin, ModelAdmin):
    list_display = ('date', 'user', 'file')
    exclude = ('metadata', 'mapping')
    inlines = [ProcessorInline]

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
    def clone(self, request, pk):
        self.object = Upload.objects.get(pk=pk)
        cloned = self.object.clone()
        url = reverse("admin:core_upload_change", args=[cloned.pk])
        return HttpResponseRedirect(url)

    @action()
    def run(self, request, pk):
        self.object = Upload.objects.get(pk=pk)
        view = Process.as_view(modeladmin=self)
        # view.kwargs = {'pk': pk}
        return view(request, pk=pk)

    @action()
    def inspect(self, request, pk):
        self.object = Upload.objects.get(pk=pk)

        with ZipFile(self.object.file, 'r') as zip_ref:
            files = sorted(filter(lambda x: not x.startswith('__MACOSX'), zip_ref.namelist()))
            workdir = tempfile.mkdtemp(dir=settings.BASE_WORK_DIR)
            zip_ref.extractall(workdir)
            targets = glob.glob(f'{workdir}/**/*.shp', recursive=True)
            shapes = {}
            for target in targets:
                with fiona.Env():
                    with fiona.open(target) as collection:
                        shapes[os.path.basename(target)] = {'meta': collection.meta,
                                                            'count': len(collection)}
                        item = next(collection.items())
                        if item:
                            item = item[1]
                            item['geometry']['coordinates'] = '...trucated...'
                            shapes[os.path.basename(target)]['sample'] = {
                                'headers': sorted(item['properties'].keys()),
                                'row': [item['properties'][k] for k in sorted(item['properties'].keys())]
                            }

        return TemplateResponse(request,
                                'admin/zipfile.html',
                                self.get_context_for_object(files=files,
                                                            shapes=shapes))


@register(UploadProcessor)
class UploadProcessorAdmin(ExtraUrlMixin, ModelAdmin):
    list_display = ('id', 'upload', 'pattern_filter',)
    form = forms.ModelForm
    inlines = [FieldMapInline]
    readonly_fields = ('state',)

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
    def inspect_shape(self, request, pk):
        workdir = None
        self.object = UploadProcessor.objects.get(pk=pk)
        try:

            with ZipFile(self.object.upload.file.path, 'r') as zip_ref:
                workdir = tempfile.mkdtemp(dir=settings.BASE_WORK_DIR)
                zip_ref.extractall(workdir)
                targets = glob.glob(f'{workdir}/{self.object.pattern_filter}',
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
        finally:
            if workdir:
                try:
                    shutil.rmtree(workdir)  # delete directory
                except OSError as exc:
                    if exc.errno != errno.ENOENT:  # ENOENT - no such file or directory
                        raise  # re-raise exception

        return TemplateResponse(request, 'admin/shapefile.html',
                                self.get_context_for_object(files=files))

    # @action()
    # def validate(self, request, pk):
    #     self.object = Upload.objects.get(pk=pk)
    #     info = self.object.validate()

    @action()
    def process(self, request, pk):
        self.object = UploadProcessor.objects.get(pk=pk)
        url = reverse("run", args=[self.object.upload.pk])
        return HttpResponseRedirect(url)

    # @link()
    # def wizard(self, request):
    #     opts = self.model._meta
    #     view = UploadWizardView.as_view(opts=opts, modeladmin=self)
    #     return view(request)
    #     # context = {'form': }
    #     # return TemplateResponse(request, "admin/upload_wizard.html", context)


class UploadFieldMapAdmin(ModelAdmin):
    search_fields = ('config', 'shape_field', 'geo_field')
