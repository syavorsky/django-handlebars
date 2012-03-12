
import os
from django_handlebars.utils import ReadableError

__all__ = ['Observer', ]

try:
    from django_handlebars.management.observer.inotify import Observer
except ImportError:
    raise ReadableError("Filesystem observing functionality is not available")


