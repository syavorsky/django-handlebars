#!/usr/bin/env python
#from distutils.core import setup
from setuptools import setup, find_packages


META_DATA = dict(
    name='django-handlebars',
    version='0.1',
    description='Handlebars for Django',
    long_description=open('README').read(),
    author='Sergii Iavorskyi',
    author_email='yavorskiy.s@gmail.com',
    url='https://github.com/yavorskiy/django_handlebars',
    keywords='django javascript test',
    classifiers=[
        "Development Status :: 4 - Beta",
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: JavaScript',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Testing',
    ],
    install_requires= ['Django>=1.3', ],
    packages=find_packages(exclude=[]),
    include_package_data=True,
    zip_safe=False,
)


if __name__ == "__main__":
    setup(**META_DATA)