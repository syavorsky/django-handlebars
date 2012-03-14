#!/usr/bin/env python
#from distutils.core import setup
from setuptools import setup, find_packages

META = dict(
    name="django-handlebars",
    version="0.1",
    description="Handlebars for Django",
    long_description=open("README.rst").read(),
    author="Sergii Iavorskyi",
    author_email="yavorskiy.s@gmail.com",
    url="https://github.com/yavorskiy/django-handlebars",
    download_url="https://github.com/yavorskiy/django-handlebars/downloads",
    license="BSD",
    keywords="django handlebars",
    packages=find_packages(exclude=[]),
    install_requires = ["django>=1.3", ],
    extras_require = {
        "Compile templates": ["python-spidermonkey",],
        "Compile templates on chnges": ["python-spidermonkey", "pyinotify"],
    },
    test_suite="runtests.runtests",
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: JavaScript",
    ],
)

if __name__ == "__main__":
    setup(**META)