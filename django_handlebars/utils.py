
import os
import sys
import re
from threading import Lock


def cant_compile():
    blockers = []
    try:
        import spidermonkey
    except ImportError:
        blockers.append('Missing "python-spidermonkey" module')
    return blockers
    
    
def cant_observe():
    blockers = []
    if sys.platform != "linux2":
        blockers.append('Available only on Linux platform with "pyinotify" module istalled')
    else:
        try:
            import pyinotify
        except ImportError:
            blockers.append('Missing "pyinotify" module')
    return blockers


def is_outdated(src_file, compiled_file):
    return not os.path.exists(compiled_file) or int(os.stat(compiled_file).st_mtime * 1000) < int(os.stat(src_file).st_mtime * 1000)


def thread_safe(func):
    lock = Lock()
    def decorated(*args, **kwargs):
        with lock:
            ret = func(*args, **kwargs)
            return ret
    return decorated


class ReadableError(Exception):
    pass


class Console(object):
    
    colors = {
        "black": "\033[30m", "red":    "\033[31m", 
        "green": "\033[32m", "yellow": "\033[33m", 
        "blue":  "\033[34m", "purple": "\033[35m", 
        "cyan":  "\033[36m", "reset":  "\033[0m"
    }
    
    def __init__(self, out=None, err=None, raw=False):
        self._out = out or sys.stdout
        self._err = err or sys.stderr
        self.raw = raw
        self.re = re.compile("<color:(%s)>" % "|".join(self.colors.keys()))
    
    def _colorize(self, match):
        return "" if self.raw else self.colors.get(match.group(1), "")
    
    def _format(self, s):
        return self.re.sub(self._colorize, "%s<color:reset>\n" % s)
    
    def set_out(self, out):
        self._out = out
    
    def set_err(self, err):
        self._err = err
    
    @thread_safe
    def out(self, s):
        self._out.write(self._format(s))
        self._out.flush()
        
    @thread_safe
    def err(self, s):
        self._err.write(self._format(s))
        self._err.flush()


class NullConsole(object):
    _stub = lambda *args, **kwargs: None
    __init__ = _stub
    set_out = _stub
    set_err = _stub
    out = _stub 
    err = _stub
    
    