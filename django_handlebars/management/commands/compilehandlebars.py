
import time
import logging
import signal

from optparse import make_option
from django.core.management.base import BaseCommand

from django_handlebars import appsettings
from django_handlebars.utils import Console, NullConsole, ReadableError, cant_compile, cant_observe


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('--debug',
            action='store_true',
            dest='debug',
            default=False,
            help='Set logging level to DEBUG'),
        make_option('--clean',
            action='store_true',
            dest='clean',
            default=False,
            help='Remove all previously compiled templates'),
        make_option('--watch',
            action='store_true',
            dest='watch',
            default=False,
            help='Watch changes with appsettings.TPL_DIR and compile'),
        make_option('--raw',
            action='store_true',
            dest='raw',
            default=False,
            help='Do not format output'),
        make_option('--quiet',
            action='store_true',
            dest='quiet',
            default=False,
            help='Do not format output'),
        )


    def warn_unavail(self, msg, reasons):
        marker = "\n  - "
        return "%s%s%s" % (msg, marker, marker.join(reasons))
    
    
    def handle(self, *command_args, **command_options):
        if command_options["debug"]:
            logging.getLogger("django_handlebars").setLevel(logging.DEBUG)
        
        console = NullConsole() if command_options["quiet"] else Console()

        try:
            console.set_out(self.stdout)
            console.set_err(self.stderr)
            console.raw = command_options["raw"]

            blockers = cant_compile()
            if blockers:
                console.err(self.warn_unavail("<color:red>You can not compile handlebars templates:<color:reset>", blockers))
                return
            
            from django_handlebars.management.compiler import Compiler
            compiler = Compiler(console=console)
            
            if command_options["clean"]:
                compiler.cleanup()
            
            if command_options["watch"]:
                blockers = cant_observe()
                if blockers:
                    console.err(self.warn_unavail("<color:red>You can not watch file changes:<color:reset>", blockers))
                    return
                
                from django_handlebars.management.observer import Observer
                
                compiler.add_path(appsettings.TPL_DIR)
                observer = Observer(appsettings.TPL_DIR, compiler)
                
                def close(signum, stack):
                    console.out("\nShutting down observer...")
                    observer.stop()
                    
                signal.signal(signal.SIGINT, close)
                observer.start()
                signal.pause()
                
            else:
                compiler.add_path(appsettings.TPL_DIR)
                compiler.terminate()
        
        except ReadableError as err:
            console.err("<color:red>Ooops!<color:reset> %s" % err.message)
            return


