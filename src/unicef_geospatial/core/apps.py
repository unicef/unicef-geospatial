from django.apps import AppConfig


class Config(AppConfig):
    name = 'unicef_geospatial.core'

    def ready(self):
        pass
