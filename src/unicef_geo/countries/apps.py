from django.apps import AppConfig


class Config(AppConfig):
    name = __name__.rpartition('.')[0]
