import logging
import logging.config
import os
import sys

from cliff.app import App
from cliff.commandmanager import CommandManager
from cliff.show import ShowOne
import cito


class CitoApp(App):
    """Cito Cliff application

    See cliff documentation to understand this."""

    def __init__(self):
        super(CitoApp, self).__init__(
            description='Data acquisition software for event building and software triggering.',
            version=cito.__version__,
            command_manager=CommandManager('cito.core.main'),
        )

    def initialize_app(self, argv):
        log_file = 'logging.conf'

        logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

        self.log = logging.getLogger(self.__class__.__name__)

        self.log.debug('Initialize application')

    def prepare_to_run_command(self, cmd):
        self.log.debug('Preparing to run command %s', cmd.__class__.__name__)

    def clean_up(self, cmd, result, err):
        self.log.debug('Clean up %s', cmd.__class__.__name__)
        if err:
            self.log.error('Got an error: %s', err)



def main(argv=sys.argv[1:]):
    if len(argv) == 0:
        print(
            "HINT: Did you mean to run 'cito process' to start building events?\n")
        argv = ['-h']
    myapp = CitoApp()

    return myapp.run(argv)
