import logging
import logging.config
import os
import sys

from cliff.app import App
from cliff.commandmanager import CommandManager
from cliff.show import ShowOne

import wax


DEFAULT_FILENAME = 'cito_file.pklz'

class WaxApp(App):

    """Wax Cliff application

    See cliff documentation to understand this."""

    def __init__(self):
        super(WaxApp, self).__init__(
            description='Data acquisition software for event building and software triggering.',
            version=wax.__version__,
            command_manager=CommandManager('wax.core.main'),
        )

    def initialize_app(self, argv):
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.debug('Initialize application')

class WaxShowOne(ShowOne):

    """Base class for all DB commands.

    Handles logging, descriptions, and common fuctions.
    """
    log = logging.getLogger(__name__)

    def get_description(self):
        return self.__doc__

    def get_parser(self, prog_name):
        parser = super(WaxShowOne, self).get_parser(prog_name)

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
    if len(argv) == 0:
        print(
            "HINT: Did you mean to run 'wax process' to start building events?\n")
        argv = ['-h']
    myapp = WaxApp()

    return myapp.run(argv)