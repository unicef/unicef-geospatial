from django.apps import AppConfig


class Config(AppConfig):
    name = 'unicef_geospatial.web'

    def ready(self):
        pass
