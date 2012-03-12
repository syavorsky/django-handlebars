import os
import logging
os.environ['DJANGO_LIVE_TEST_SERVER_ADDRESS'] = 'localhost:8088'

from unittest import skipIf
from django.test import TestCase
from django.test import LiveServerTestCase
from django.test.utils import override_settings

import appsettings   

# settings test
import urllib2

# tags test
import time
from django.template import Template, Context

# templates compilation
from django_handlebars.utils import cant_compile, cant_observe
from django.core.management import call_command

# compiling and observing
from django_handlebars.utils import ReadableError
import tempfile
import shutil


CANT_COMPILE = "; ".join(cant_compile())
CANT_OBSERVE = "; ".join(cant_observe())



def compiled_mode(on=False):
    def decorator(func):
        def decorated(self, *args, **kwargs):
            with self.settings(HANDLEBARS_COMPILED=on):
                reload(appsettings)
                func(self, *args, **kwargs)
        return decorated
    return decorator



class SettingsTest(LiveServerTestCase):
    
    def test_paths(self):
        self.assertTrue(os.access(appsettings.TPL_DIR, os.R_OK), "appsettings.TPL_DIR path is not readable")
        self.assertTrue(os.access(appsettings.TPL_CMPDIR, os.W_OK), "appsettings.TPL_CMPDIR '%s' path is not writeable" % appsettings.TPL_CMPDIR)
        self.assertTrue(os.access(appsettings.SCRIPT_PATH, os.R_OK), "appsettings.SCRIPT_PATH path is not readable")
        
    def test_urls(self):
        for script in ["handlebars.js", "handlebars.runtime.js", "handlebars.django.js"] + appsettings.SCRIPT_EXTRAS:
            url = self.live_server_url + appsettings.SCRIPT_URL + script
            try:
                result = urllib2.urlopen(url)
            except urllib2.HTTPError:
                result = None
                pass
            self.assertIsNotNone(result, 'Missing script "appsettings.SCRIPT_URL/%s"' % script)
        


class TagsTest(TestCase):
    
    def _html(self, tag):
        return Template("{%% load handlebars_tags %%}{%% %s %%}" % tag).render(Context())
    
    @classmethod
    def setUpClass(cls):
        cls.spec = time.strftime("test-tags-%H.%M.%S")
        cls.tplpath = "%s.html" % os.path.join(appsettings.TPL_DIR, cls.spec)
        
        with open(cls.tplpath, "w") as f:
            f.write("whatever")
    
    @classmethod
    def tearDownClass(cls):
        os.remove(cls.tplpath)
        
    def setUp(self):
        with self.settings(HANDLEBARS_COMPILED=False):
            reload(appsettings)
    
    def test_handlebars_scripts(self):
        html = self._html("handlebars_scripts")
        self.assertNotEqual(html.find("{tpl}.html"), -1, "Template load URL is not pointed to .html when COMPILED=False")
        self.assertNotEqual(html.find("handlebars.js"), -1, "Doesn't include Handlebars parser when COMPILED=False")
    
    @compiled_mode(True)
    def test_handlebars_scripts_compiled(self):
        html = self._html("handlebars_scripts")
        self.assertNotEqual(html.find("{tpl}.js"), -1, "Template load URL is not pointed to .js templates when COMPILED=True")
        self.assertNotEqual(html.find("handlebars.runtime.js"), -1, "Doesn't include Handlebars.runtime when COMPILED=True")
        
    def test_handlebars_template(self):
        html = self._html('handlebars_template "not/existing/template"')
        self.assertNotEquals(html.find("Invalid template spec"), -1, "Passing invalid template spec")
        
    def test_handlebars_template_found(self):
        html = self._html('handlebars_template "%s"' % self.spec)
        self.assertEqual(html.find("Invalid template spec"), -1, "Failed to include template by spec")
        
    @compiled_mode(True)
    def test_handlebars_template_missing_compiled(self):
        html = self._html('handlebars_template "%s"' % self.spec)
        self.assertNotEquals(html.find("Invalid template spec"), -1, "Passed inclusion of non existing compiled template")
        
    def test_handlebars_template_tolerate_abspath(self):
        html = self._html('handlebars_template "/%s"' % self.spec)
        self.assertEquals(html.find("Invalid template spec"), -1, "Doesn't tolerate template specs starting with slash")
    
    def test_handlebars_template_safe_path(self):        
        html = self._html('handlebars_template "../../%s"' % self.spec)
        self.assertNotEquals(html.find("Invalid template spec"), -1, "Passed template spec pointed to outside of appsettings.TPL_DIR")



@skipIf(CANT_COMPILE, CANT_COMPILE)
class CompilerTest(TestCase):
    
    @classmethod
    def setUpClass(cls):
        from django_handlebars.management.compiler import Compiler
        
        cls.src_dir = tempfile.mkdtemp(prefix="compiler-test-sources-")
        cls.cmp_dir = tempfile.mkdtemp(prefix="compiler-test-compiled-")
        cls.compiler = Compiler(cls.src_dir, cls.cmp_dir)
    
    @classmethod
    def tearDownClass(cls):
        cls.compiler.terminate()
        shutil.rmtree(cls.src_dir)
        shutil.rmtree(cls.cmp_dir)
    
    def test_security(self):
        outside_dir = tempfile.mkdtemp(prefix="compiler-test-outside-")
        fd, path = tempfile.mkstemp(dir=outside_dir, suffix=".html")
        with open(path, "w") as fd:
            fd.write("whatever")
        
        time.sleep(1)
        self.assertRaisesRegexp(ReadableError, "outside", self.compiler.add_path, outside_dir)
        shutil.rmtree(outside_dir)
    
    def test_add_file(self):
        fd, path_from = tempfile.mkstemp(dir=self.src_dir, suffix=".html")
        with open(path_from, "w") as fd:
            fd.write("whatever")

        path_to = self.compiler.translate_path(path_from)
        self.compiler.add_path(path_from)
        
        time.sleep(1)
        self.assertTrue(os.path.exists(path_to), "Compiler failed to compile single file")
        
        with open(path_to) as fd:
            self.assertNotEqual(fd.read().find('function'), -1, "Compiled file is invalid")
            
    def test_remove_file(self):
        fd, path_from = tempfile.mkstemp(dir=self.src_dir, suffix=".html")
        with open(path_from, "w") as fd:
            fd.write("whatever")

        path_to = self.compiler.translate_path(path_from)
        with open(path_to, "w") as fd:
            fd.write("whatever")
        
        self.compiler.remove_path(path_from)
        
        time.sleep(1)
        self.assertFalse(os.path.exists(path_to), "Compiled file remains after source deleted")
    
    def test_add_dir(self):
        dir = tempfile.mkdtemp(prefix="subdir-", dir=self.src_dir)
        
        paths = range(3)
        for i in paths:
            fd, paths[i] = tempfile.mkstemp(dir=dir, suffix=".html")
            with open(paths[i], "w") as fd:
                fd.write("whatever")

        self.compiler.add_path(dir)
        
        time.sleep(1)
        for path_from in paths:
            path_to = self.compiler.translate_path(path_from)
            self.assertTrue(os.path.exists(path_to), "Compiler failed to compile dir")
        
            with open(path_to) as fd:
                self.assertNotEqual(fd.read().find('function'), -1, "Compiled file is invalid when compiling dir")
                
    def test_remove_dir(self):
        dir = tempfile.mkdtemp(prefix="subdir-", dir=self.src_dir)
        dir_to = self.compiler.translate_path(dir)
        os.mkdir(dir_to)
        
        paths = range(3)
        for i in paths:
            fd, paths[i] = tempfile.mkstemp(dir=dir, suffix=".html")
            with open(paths[i], "w") as fd:
                fd.write("whatever")
            
            path_to = self.compiler.translate_path(paths[i])
            with open(path_to, "w") as fd:
                fd.write("whatever")
        
        self.compiler.remove_path(dir)

        time.sleep(1)
        self.assertFalse(os.path.exists(dir_to), "Compiler failed to compile dir")
            


@skipIf(CANT_OBSERVE, CANT_OBSERVE)
class ObserverTest(TestCase):
    @classmethod
    def setUpClass(cls):
        from django_handlebars.management.compiler import CompilerMock
        from django_handlebars.management.observer import Observer
        
        cls.src_dir = tempfile.mkdtemp(prefix="observer-test-sources-")
        cls.cmp_dir = tempfile.mkdtemp(prefix="observer-test-compiled-")
        
        cls.compiler = CompilerMock()
        cls.observer = Observer(cls.src_dir, cls.compiler)
        cls.observer.start()
                
    @classmethod
    def tearDownClass(cls):
        cls.observer.stop()
        shutil.rmtree(cls.src_dir)
        shutil.rmtree(cls.cmp_dir)
    
    def test_file_create(self):
        fd, path = tempfile.mkstemp(dir=self.src_dir, suffix=".html")
        with open(path, "w") as fd:
            fd.write("whatever");
        
        time.sleep(1)
        self.assertGreater(self.compiler.stat("add_path", path), 0, "Observer missed file creation")
        
    def test_file_move(self):
        fd, path_from = tempfile.mkstemp(dir=self.src_dir, suffix=".html")
        path_to = path_from.replace(".html", "-renamed.html")
        with open(path_from, "w") as fd:
            fd.write("whatever");
        
        shutil.move(path_from, path_to)

        time.sleep(1)
        self.assertGreater(self.compiler.stat("remove_path", path_from), 0, "Observer missed old file deletion while renaming")
        self.assertGreater(self.compiler.stat("add_path", path_to), 0, "Observer missed new file creation while renaming")

    def test_file_delete(self):
        fd, path = tempfile.mkstemp(dir=self.src_dir, suffix=".html")
        with open(path, "w") as fd:
            fd.write("whatever");
        os.remove(path)
        
        time.sleep(1)
        self.assertGreater(self.compiler.stat("add_path", path), 0, "Observer missed file creation")
        
    def test_dir_move(self):
        dir_from = tempfile.mkdtemp(prefix="subdir-", dir=self.src_dir)
        dir_to = dir_from.replace("subdir-", "subdir-renamed-")
    
        paths = range(3)
        for i in paths:
            fd, paths[i] = tempfile.mkstemp(dir=dir_from, suffix=".html")
            with open(paths[i], "w") as fd:
                fd.write("whatever");
        
        time.sleep(1)
        shutil.move(dir_from, dir_to)
                
        time.sleep(1)
        self.assertGreater(self.compiler.stat("remove_path", dir_from), 0, "Observer missed old dir deletion while renaming dir")
        self.assertGreater(self.compiler.stat("add_path", dir_to), 0, "Observer missed new dir creation while renaming dir")
        
    def test_dir_remove(self):
        dir = tempfile.mkdtemp(prefix="subdir-", dir=self.src_dir)
        
        time.sleep(1)
        os.rmdir(dir)
                
        time.sleep(1)
        self.assertGreater(self.compiler.stat("remove_path", dir), 0, "Observer missed old file deletion while renaming dir")









