
"""
Any configuration setting listed in __all__ may be overriden
in settings.py by defining variable with same name and 
prefixed with "HANDLEBARS_"
"""

import os
import re
from django.conf import settings
from django_handlebars.utils import cant_compile

root = os.path.dirname(__file__)
path = lambda p: os.path.join(root, p[:-1] if p.endswith("/") else p)

__all__ = ("NUM_THREADS", "COMPILED",
    "TPL_DIR", "TPL_CMPDIR", "TPL_MASK", "TPL_URL", "TPL_JSWRAPPER",
    "SCRIPT_PATH", "SCRIPT_EXTRAS", "SCRIPT_TPL",)

# Tells whether compiled or raw templates should be used in browser
# By default it assumes True if required packages installed
COMPILED = len(cant_compile()) == 0

# How many threads to spawn in Compiler 
NUM_THREADS = 4

# Raw templates file name mask. This is used in compilehandlebars --watch
# to handle filesystem events involving tergeting files only
TPL_MASK = "\w+.html$"

# Raw templates directory
TPL_DIR = path("static/js/templates-src")

# Compiled templates directory
TPL_CMPDIR = path("static/js/templates")

# Raw templates URL. Templates are loaded as regular static files,
# no dynamic views involved. Point it to some view if you have different idea.
# Make sure you kept %%s, which is placeholder for template spec 
TPL_URL = "%sjs/templates-src/%%s.html" % settings.STATIC_URL

# Compiled templates URL
TPL_CMPURL = "%sjs/templates/%%s.js" % settings.STATIC_URL

# Optional callable wrapping compiled template
# and returning string to written into file
TPL_JSWRAPPER = None

# File system path to the directory storing handlebars.js
# and scripts listed in SCRIPT_EXTRAS. This is used by Compiler
# to load Handlebars engine into SpiderMonkey container
SCRIPT_PATH = path("static/js/handlebars")

# Base URL for handlebars.js, handlebars.runtime.js and handlebars.django.js
SCRIPT_URL = "%sjs/handlebars/" % settings.STATIC_URL

# Script filenames you want to load into SpiderMonkey 
# along with handlebars.js. This might be custom Handlebars Helpers or something
SCRIPT_EXTRAS = []

# Wrapping string for including templates on page. 
# This will be gone in the next version 
SCRIPT_TPL = "Handlebars.tpl('%(namespace)s', %(compiled)s);"

loacal_vars = locals()
for var in __all__:
    global_var = "HANDLEBARS_%s" % var
    if hasattr(settings, global_var):
        loacal_vars[var] = getattr(settings, global_var)
        
SCRIPT_CONF = {
    "loadurl": (TPL_CMPURL if COMPILED else TPL_URL) % '{tpl}',
}
