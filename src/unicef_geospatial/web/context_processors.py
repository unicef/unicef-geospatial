# -*- coding: utf-8 -*-
from django.conf import settings


def sett(request):
    return {'settings': settings}
