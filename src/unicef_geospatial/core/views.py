import glob
import os
import tempfile
from collections import OrderedDict
from zipfile import ZipFile

from cfgv import ValidationError
from django import forms
from django.conf import settings
from django.contrib.admin.options import get_content_type_for_model
from django.core.files.storage import FileSystemStorage
from django.forms import inlineformset_factory, BaseInlineFormSet
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.views.generic import DetailView

import fiona
from formtools.wizard.views import SessionWizardView

from unicef_geospatial.core.forms.upload import (
    ConfigureForm,
    PreviewForm,
    SelectFilesForm,
    UploadFieldMapForm,
    UploadForm,
)
from unicef_geospatial.core.models import Country, Upload, UploadFieldMap, UploadProcessor
from unicef_geospatial.core.models.upload import sane_repr
from unicef_geospatial.state import state


def index(request):
    context = {'page': 'index', 'title': 'Geospatial Server'}
    return TemplateResponse(request, 'index.html', context)


class FieldMapInlineFormSet(BaseInlineFormSet):
    def clean(self):
        self.validate_unique()
        if hasattr(self, 'cleaned_data'):
            provided = set([k.get('geo_field','') for k in self.cleaned_data])
            required = {'country', 'level', 'parent'}
            missing = required - provided
            if missing:
                raise forms.ValidationError("Missing required field %s" % sane_repr(missing))


COL_MAPPING = 10


def form_list_factory(levels=5):
    conditions = {'start': True,
                  'preview': True}
    form_list = [('start', UploadForm),
                 ('select', SelectFilesForm),
                 ]

    for i in range(0, levels):
        form_list.append(['config:%s' % i, ConfigureForm])
        form_list.append(['fields:%s' % i, inlineformset_factory(UploadProcessor,
                                                                 UploadFieldMap,
                                                                 form=UploadFieldMapForm,
                                                                 formset=FieldMapInlineFormSet,
                                                                 fields=('geo_field',
                                                                         'shape_field',
                                                                         'is_value',
                                                                         'mandatory'),
                                                                 # check get_form_initial()
                                                                 # when change `extra`
                                                                 extra=COL_MAPPING)])

        conditions['config:%s' % i] = True
        conditions['fields:%s' % i] = True
    form_list.append(['preview', PreviewForm])
    return form_list, conditions


def get_shape_field_cleaned_data(cleaned_data, field):
    for k, v in cleaned_data.items():
        if v['geo_field'] == field:
            return v['shape_field']


class UploadWizardView(SessionWizardView):
    form_list, condition_dict = form_list_factory(5)

    opts = None
    modeladmin = None
    file_storage = FileSystemStorage(os.path.join(settings.BASE_WORK_DIR, 'wizard_storage'))

    def get_form_list(self):
        form_list = OrderedDict()
        for form_key, form_class in self.form_list.items():
            # try to fetch the value from condition list, by default, the form
            # gets passed to the new list.
            if ':' in form_key and 'selected_files' in self.storage.data:
                t, idx = form_key.split(":")
                condition = self.storage.data['selected_files'].get('file_%s' % idx, False)
            else:
                condition = self.condition_dict.get(form_key, True)
            if callable(condition):
                # call the value if needed, passes the current instance.
                condition = condition(self)
            if condition:
                form_list[form_key] = form_class
        return form_list

    def inspect_shape(self, shapefile):
        targets = glob.glob(f"{self.storage.data['workdir']}/**/{shapefile}", recursive=True)
        if len(targets) != 1:
            raise ValueError(f'"{shapefile}" must match only one file')
        with fiona.Env():
            with fiona.open(targets[0]) as collection:
                info = {'shapefile': shapefile,
                        'meta': collection.meta,
                        'count': len(collection)}
                item = next(collection.items())
                if item:
                    item = item[1]
                    item['geometry']['coordinates'] = '...trucated...'
                    info['sample'] = item
        return info

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form, **kwargs)
        context['data'] = self.storage.data
        if self.modeladmin:
            modeladmin = self.modeladmin
            opts = self.opts
            context.update({
                'has_view_permission': modeladmin.has_view_permission(self.request, None),
                'has_add_permission': modeladmin.has_add_permission(self.request),
                'has_change_permission': modeladmin.has_change_permission(self.request, None),
                'has_delete_permission': modeladmin.has_delete_permission(self.request, None),
                'opts': opts,
                'content_type_id': get_content_type_for_model(Upload).pk,
                'save_as': modeladmin.save_as,
                'save_on_top': modeladmin.save_on_top,

                'app_label': opts.app_label,
            })

        if 'preview:' in self.steps.current:
            context['all_data'] = self.get_all_cleaned_data()
        elif 'fields:' in self.steps.current:
            t, idx = self.steps.current.split(":")
            shapefile = self.storage.data['shapes'][idx]
            zipfile = self.storage.data['zipfile']
            context.update({'zipfile': zipfile,
                            'shapes': self.storage.data['shapes'],
                            'files': self.storage.data['files'],
                            'current_file': int(idx) + 1,
                            'shapefile': shapefile,
                            'info': self.inspect_shape(shapefile)
                            })

        return context

    def process_step_files(self, form):
        ret = self.get_form_step_files(form)
        if 'workdir' not in self.storage.data:
            self.storage.data['workdir'] = tempfile.mkdtemp(dir=settings.BASE_WORK_DIR)
        if isinstance(form, UploadForm):
            shapefile = ret['start-file']
            with ZipFile(shapefile.file.name, 'r') as zip_ref:
                zip_ref.extractall(self.storage.data['workdir'])
                files = sorted(filter(lambda x: not x.startswith('__MACOSX'), zip_ref.namelist()))
                shapes = {i: v for i, v in enumerate(sorted(filter(lambda x: x.endswith('.shp'), files)))}

            self.storage.data['shapes'] = shapes
            self.storage.data['files'] = []
            self.storage.data['zipfile'] = shapefile.name

        return ret

    def process_step(self, form):
        data = form.cleaned_data
        if isinstance(form, SelectFilesForm):
            self.storage.data['selected_files'] = data
            self.storage.data['shapes'] = {i: v for i, v in self.storage.data['shapes'].items() if data['file_%s' % i]}
        if isinstance(data, list):
            for record in data:
                if record.get('geo_field', '') == 'country':
                    self.storage.data['country_col'] = record.get('shape_field', '')
                    self.storage.data['country_is_value'] = record.get('is_value', False)
        return super().process_step(form)

    def get_form_initial(self, step):
        initial = self.initial_dict.get(step, {})
        BASE = {i: {} for i in range(COL_MAPPING)}
        if step not in ['start', 'preview', 'select']:
            t, idx = step.split(":")
            idx = int(idx)
            if t == 'config':
                initial.update({"boundary_type_policy": 'get_or_create',
                                "country_policy": 'get_or_create',
                                "pattern_filter": self.storage.data['shapes'][str(idx)]
                                })
            elif t == 'fields':
                BASE[0] = {"geo_field": 'country',
                           "shape_field": 'COUNTRY'}
                BASE[1] = {"geo_field": 'level',
                           "shape_field": idx}

                if idx == 0:
                    initial.update(BASE)
                else:
                    BASE[0] = {"geo_field": 'country',
                               "shape_field": self.storage.data.get('country_col', None)}
                    BASE[2] = {"geo_field": 'p_code', "shape_field": 'P_CODE'}
                    BASE[3] = {"geo_field": 'boundary_type',
                               "shape_field": 'ADM%s_PCODE' % idx}
                    BASE[4] = {"geo_field": 'parent',
                               "shape_field": 'ADM%s_PCODE' % (idx - 1)}
                    initial.update(BASE)
            return initial

    def get_form_kwargs(self, step=None):
        if step and step == 'select':
            return {'shapefiles': self.storage.data['shapes']}
        elif step and 'fields:' in step:
            return {'queryset': UploadProcessor.objects}
        return super().get_form_kwargs(step)

    def get_form(self, step=None, data=None, files=None):
        frm = super().get_form(step, data, files)
        if step and 'fields:' in step:
            t, idx = step.split(":")
            prev = 'config:%s' % idx
            parent = self.get_cleaned_data_for_step(prev)
            frm.instance.pattern_filter = parent['pattern_filter']

        return frm

    def get_template_names(self):
        if self.steps.current in ['start', 'preview', 'select']:
            return ["upload/%s.html" % self.steps.current,
                    "upload/base.html"]
        t, idx = self.steps.current.split(":")
        return ["upload/%s.html" % t, "upload/base.html"]

    def done(self, form_list, **kwargs):
        form_list = list(form_list)
        master_form = form_list[0]
        # fields_mapping = form_list[1]
        # upload_form = form_list[2]
        saved = []
        master_form.instance.user = state.request.user
        master = master_form.save()
        saved.append(master)
        for i in range(2, len(form_list[1:-1]), 2):
            form = form_list[i]
            form.instance.upload = master
            processor = form.save()
            saved.append(processor)

            form = form_list[i + 1]
            form.instance = processor
            field_map = form.save()
            saved.append(field_map)
        #
        # fields_mapping.instance = master
        # fields_mapping.save()
        return render(self.request, 'upload/summary.html', {'object': master,
                                                            'saved_list': saved})


class Process(DetailView):
    model = Upload

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
