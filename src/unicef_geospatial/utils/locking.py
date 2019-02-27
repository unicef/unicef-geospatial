import warnings

from django.conf import settings
from django.core.cache import caches
from django.db import ProgrammingError


class Lock:
    def acquire(self, *args, **kwargs):
        warnings.warn("Dummy lock acquired")
        return self

    def release(self, *args, **kwargs):
        pass


def lock(*args, **kwargs):
    locks = caches['lock']
    if hasattr(locks, 'lock'):
        return locks.lock()
    elif settings.DEBUG:
        return Lock()
    else:
        raise ProgrammingError("Cannot use dummy locking if DEBUG=False")
