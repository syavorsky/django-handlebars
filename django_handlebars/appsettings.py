
import os
import re
from django.conf import settings
from django_handlebars.utils import cant_compile

root = os.path.dirname(__file__)
path = lambda p: os.path.join(root, p[:-1] if p.endswith("/") else p)

__all__ = ("NUM_THREADS", "COMPILED",
    "TPL_DIR", "TPL_CMPDIR", "TPL_MASK", "TPL_URL", 
    "SCRIPT_PATH", "SCRIPT_EXTRAS", "SCRIPT_TPL", "SCRIPT_CONF",)

COMPILED = len(cant_compile()) == 0
NUM_THREADS = 4

TPL_MASK = "\w+.html$"
TPL_DIR = path("static/js/templates-src")
TPL_CMPDIR = path("static/js/templates")
TPL_URL = "%sjs/templates-src/%%s.html" % settings.STATIC_URL
TPL_CMPURL = "%sjs/templates/%%s.js" % settings.STATIC_URL

SCRIPT_PATH = path("static/js/handlebars")
SCRIPT_URL = "%sjs/handlebars/" % settings.STATIC_URL
SCRIPT_EXTRAS = []
SCRIPT_TPL = "Handlebars.tpl('%(namespace)s', %(compiled)s);"

loacal_vars = locals()
for var in __all__:
    global_var = "HANDLEBARS_%s" % var
    if hasattr(settings, global_var):
        loacal_vars[var] = getattr(settings, global_var)
        
SCRIPT_CONF = {
    "loadurl": (TPL_CMPURL if COMPILED else TPL_URL) % '{tpl}',
}