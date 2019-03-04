from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.db import models


class UpdateMetaData(models.Model):
    date = models.DateField(auto_now_add=True)
    user = models.ForeignKey(User, models.CASCADE)
    mapping = JSONField()
