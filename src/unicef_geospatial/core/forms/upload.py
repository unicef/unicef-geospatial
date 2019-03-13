from functools import lru_cache

from crispy_forms.helper import FormHelper
from django import forms

from unicef_geospatial.core.models import Upload, UploadFieldMap, BoundaryType, Country, UploadProcessor


class UploadCreateForm(forms.ModelForm):
    class Meta:
        model = Upload
        fields = ('user',)


def get_boundary_fields():
    from unicef_geospatial.core.models import Boundary
    elements = ['']+[f.name for f in Boundary._meta.get_fields()] \
        + ['boundary_type__%s' % f.name for f in BoundaryType._meta.get_fields()] \
        + ['country__%s' % f.name for f in Country._meta.get_fields()]
    return zip(elements, elements)


class UploadFieldMapForm(forms.ModelForm):

    class Meta:
        model = UploadFieldMap
        fields = ('geo_field', 'shape_field', 'mandatory', 'is_value')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False


class UploadForm(forms.ModelForm):
    class Meta:
        model = Upload
        fields = ('file',)


class SelectFilesForm(forms.Form):

    def __init__(self, shapefiles, **kwargs):
        self.shapefiles = shapefiles
        super().__init__(**kwargs)
        for k, v in self.shapefiles.items():
            self.fields['file_{index}'.format(index=k)] = forms.BooleanField(
                label=v, required=False
            )


class ConfigureForm(forms.ModelForm):
    class Meta:
        model = UploadProcessor
        fields = ('pattern_filter', 'boundary_type_policy', 'country_policy')


class PreviewForm(forms.Form):
    pass

