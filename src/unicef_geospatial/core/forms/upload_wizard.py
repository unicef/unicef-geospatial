from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.contrib.admin.options import get_content_type_for_model
from django.core.files.storage import DefaultStorage, FileSystemStorage
from django.forms import inlineformset_factory, modelform_factory
from django.shortcuts import render
from formtools.preview import FormPreview
from formtools.wizard.views import SessionWizardView

from unicef_geospatial.core.models import Upload, Country, UploadFieldMap
from unicef_geospatial.state import state


class SelectType(forms.ModelForm):
    class Meta:
        model = Upload
        fields = ('country', 'country_field', 'pattern_filter',
                  'boundary_type_policy','country_policy')


class UploadForm(forms.ModelForm):
    class Meta:
        model = Upload
        fields = ('file',)


class SummaryForm(forms.ModelForm):
    class Meta:
        model = Upload
        fields = ('country_field', 'country', )



class UploadWizardView(SessionWizardView):
    template_name = "admin/upload_wizard.html"
    form_list = [SelectType,
                 # SelectCountry,
                 # SelectCountryFieldName,
                 inlineformset_factory(Upload, UploadFieldMap,
                                       fields=('geo_field',
                                               'shape_field',
                                               'is_value',
                                               'mandatory'),
                                       extra=10),
                 UploadForm,
                 # FormPreview(modelform_factory(Upload, exclude=('user',)))
                 ]
    # condition_dict = {'1': show_selectcountry,
    #                   '2': show_selectcountryfieldname}
    opts = None
    modeladmin = None
    file_storage = FileSystemStorage('/data/PROGETTI/UNICEF/unicef-geospatial/~build/storage')

    def get_context_data(self, form, **kwargs):
        modeladmin = self.modeladmin
        opts = self.opts
        context = super().get_context_data(form, **kwargs)
        context.update({
            # 'add': add,
            # 'change': change,
            'has_view_permission': modeladmin.has_view_permission(self.request, None),
            'has_add_permission': modeladmin.has_add_permission(self.request),
            'has_change_permission': modeladmin.has_change_permission(self.request, None),
            'has_delete_permission': modeladmin.has_delete_permission(self.request, None),
            # # 'has_editable_inline_admin_formsets': has_editable_inline_admin_formsets,
            # 'has_file_field': context['adminform'].form.is_multipart() or any(
            #     admin_formset.formset.form().is_multipart()
            #     for admin_formset in context['inline_admin_formsets']
            # ),
            # 'has_absolute_url': view_on_site_url is not None,
            # 'absolute_url': view_on_site_url,
            # 'form_url': form_url,
            'opts': opts,
            'content_type_id': get_content_type_for_model(Upload).pk,
            'save_as': modeladmin.save_as,
            'save_on_top': modeladmin.save_on_top,
            # 'to_field_var': modeladmin.TO_FIELD_VAR,
            # 'is_popup_var': modeladmin.IS_POPUP_VAR,
            'app_label': opts.app_label,
        })
        return context

    def get_form(self, step=None, data=None, files=None):
        frm = super().get_form(step, data, files)
        if isinstance(frm, UploadForm):
            # frm.instance.country =
            frm.instance.country_field = 'aaa'
        # TODO: remove me
        print(111, "upload_wizard.py:87", step, frm.__class__, frm.instance)

        return frm

    # def get_form_initial(self, step):
        # step0 = self.storage.get_step_data('0') or {}
        # step1 = self.storage.get_step_data('1') or {}
        # step2 = self.storage.get_step_data('2') or {}
        # initial = self.initial_dict.get(step, {})
        # if step == '4':
        #     initial.update({"type_of_upload": step0.get('0-type_of_upload'),
        #                     "country": step1.get('1-country'),
        #                     "country_field": step2.get('0-country_field'),
        #                     })
        # return initial

    def process_step(self, form):
        return super().process_step(form)

    def get_template_names(self):
        if self.steps.current == '1':
            return ["admin/upload_wizard2.html"]
        return ["admin/upload_wizard.html"]

    def done(self, form_list, **kwargs):
        form_list = list(form_list)
        master_form = form_list[0]
        fields_mapping = form_list[1]
        upload_form = form_list[2]
        master_form.instance.user = state.request.user
        master_form.instance.file = upload_form.instance.file

        master = master_form.save()

        fields_mapping.instance = master
        fields_mapping.save()
        return render(self.request, 'admin/upload_summary.html', {'object': master})
