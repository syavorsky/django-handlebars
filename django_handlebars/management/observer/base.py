
import os

class BaseObserver(object):
    
    def __init__(self, source_dir, compiler):
        if not os.access(source_dir, os.R_OK):
            raise OSError('Dir "%s" is not readable' % source_dir)
        self.source_dir = source_dir
        self.compiler = compiler
    
    def start(self):
        raise NotImplemented("Method start() must be implemented in subclass")
    
    def stop(self):
        raise NotImplemented("Method stop() must be implemented in subclass")
        
