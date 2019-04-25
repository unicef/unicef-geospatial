from django.conf import settings
from django.db import models

from crashlog.middleware import process_exception

from unicef_geospatial.state import state


class CurrentUserField(models.ForeignKey):
    def __init__(self, **kwargs):
        kwargs['to'] = settings.AUTH_USER_MODEL
        kwargs['on_delete'] = models.CASCADE
        kwargs['null'] = True
        kwargs['blank'] = True
        kwargs['editable'] = False
        super().__init__(**kwargs)

    def get_default(self):
        try:
            return state.request.user
        except Exception as e:
            process_exception(e)
            return None


class CreatorUserField(CurrentUserField):

    def __init__(self, **kwargs):
        kwargs.setdefault('related_name', '+')
        super().__init__(**kwargs)

    def get_db_prep_save(self, value, connection):
        try:
            if value is None or (value == ''):
                return state.request.user.pk
            return super().get_db_prep_save(value, connection)
        except Exception:
            return None


class ModifierUserField(CurrentUserField):
    def __init__(self, **kwargs):
        kwargs.setdefault('related_name', '+')
        super().__init__(**kwargs)

    def get_db_prep_save(self, value, connection):
        return state.request.user.pk
