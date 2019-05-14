# import json
import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unicef_geospatial.config.settings')


class DatamartCelery(Celery):
    _mapping = {}

    def get_all_etls(self):
        return [cls for (name, cls) in self.tasks.items() if hasattr(cls, 'linked_model')]


app = Celery('geospatial')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
