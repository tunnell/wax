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
        used_file_config = False
        if os.path.exists(log_file):
            logging.config.fileConfig(log_file)
            used_file_config = True

        self.log = logging.getLogger(self.__class__.__name__)
        if used_file_config:
            logging.info("Loaded logging configuration: %s", log_file)
        self.log.debug('Initialize application')

    def prepare_to_run_command(self, cmd):
        self.log.debug('Preparing to run command %s', cmd.__class__.__name__)

    def clean_up(self, cmd, result, err):
        self.log.debug('Clean up %s', cmd.__class__.__name__)
        if err:
            self.log.error('Got an error: %s', err)


class CitoShowOne(ShowOne):
    """Base class for all DB commands.

    Handles logging, descriptions, and common fuctions.
    """
    log = logging.getLogger(__name__)

    def get_description(self):
        return self.__doc__

    def get_parser(self, prog_name):
        parser = super(CitoShowOne, self).get_parser(prog_name)

        parser.add_argument("--hostname", help="MongoDB database address",
                            type=str,
                            default='127.0.0.1')

        return parser

    def get_status(self, db):
        """Return DB errors, if any"""
        columns = ['Status']
        error = db.error()
        if error:
            self.log.error(error)
            data = [error]
        else:
            data = ['success']
        return columns, data


def main(argv=sys.argv[1:]):
    myapp = CitoApp()
    return myapp.run(argv)