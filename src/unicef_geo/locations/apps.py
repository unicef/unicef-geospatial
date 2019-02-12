from django.apps import AppConfig


class Config(AppConfig):
    label = "locations"
    name = __name__.rpartition('.')[0]
