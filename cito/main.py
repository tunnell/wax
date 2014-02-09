import logging
import logging.config
import os
import sys

import cito
from cliff.app import App
from cliff.commandmanager import CommandManager


class CitoApp(App):

    def __init__(self):
        super(CitoApp, self).__init__(
            description='cito DAQ software.',
            version=cito.__version_string__,
            command_manager=CommandManager('cito.main'),
        )

    def initialize_app(self, argv):
        log_file = 'logging.conf'
        used_file_config = False
        if os.path.exists(log_file):
            logging.config.fileConfig(log_file)
            used_file_config = True

        self.log = logging.getLogger(self.__class__.__name__)
        if used_file_config:
            logging.info("Loaded logging configuration: %s", log_file)
        self.log.debug('Initialize application')

    def prepare_to_run_command(self, cmd):
        self.log.info('Preparing to run command %s', cmd.__class__.__name__)

    def clean_up(self, cmd, result, err):
        self.log.debug('Clean up %s', cmd.__class__.__name__)
        if err:
            self.log.error('Got an error: %s', err)


def main(argv=sys.argv[1:]):
    myapp = CitoApp()
    return myapp.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
