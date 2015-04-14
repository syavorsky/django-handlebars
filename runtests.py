#!/usr/bin/env python
import os
import sys

from django.conf import settings

if not settings.configured:
    settings.configure(
        STATIC_URL = '/static/',
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.admin',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.sites',

            'django_handlebars',
        ],
    )

try:
    from django import setup
except ImportError:
    pass
else:
    setup()

try:
    from django.test.runner import DiscoverRunner as Runner
except ImportError:
    from django.test.simple import DjangoTestSuiteRunner as Runner



def runtests(*args, **kwargs):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    test_runner = Runner(**kwargs)
    failures = test_runner.run_tests(["django_handlebars"])
    sys.exit(failures)

if __name__ == '__main__':
    runtests()
