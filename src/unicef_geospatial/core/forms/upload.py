from django.forms import ModelForm

from unicef_geospatial.core.models import Upload


class UploadCreateForm(ModelForm):
    class Meta:
        model = Upload
        fields = ('user', )
