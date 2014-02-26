import logging
import logging.config
import os
import sys
import math
import time
from tqdm import tqdm

from cliff.app import App
from cliff.command import Command
from cliff.commandmanager import CommandManager
from cliff.show import ShowOne
from cito.Database import InputDBInterface
import cito


class CitoApp(App):
    """Cito Cliff application

    See cliff documentation to understand this."""

    def __init__(self):
        super(CitoApp, self).__init__(
            description='cito DAQ software.',
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


def main(argv=sys.argv[1:]):
    myapp = CitoApp()
    return myapp.run(argv)


class CitoCommand(Command):
    """CitoSingleCommand base class

    This only looks over some range t0 till t1
    """

    def get_description(self):
        return self.__doc__

    def get_parser(self, prog_name):
        parser = super(CitoCommand, self).get_parser(prog_name)

        parser.add_argument("--hostname", help="MongoDB database address",
                            type=str,
                            default='127.0.0.1')

        parser.add_argument('--chunksize', type=int,
                            help="Size of data chunks to process [10 ns step]",
                            default=2 ** 24)
        parser.add_argument('--padding', type=int,
                            help='Padding to overlap processing windows [10 ns step]',
                            default=10 ** 2)

        return parser

    def get_tasks(self):
        raise NotImplementedError()

    def take_action(self, parsed_args):
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.debug('Initialized %s', self.__class__.__name__)

        chunk_size = parsed_args.chunksize
        padding = parsed_args.padding

        self.log.debug('Args: %s', str(parsed_args))

        conn, my_db, collection = InputDBInterface.get_db_connection(hostname=parsed_args.hostname)

        min_time = InputDBInterface.get_min_time(collection)

        self.take_action_wrapped(chunk_size, padding, min_time,
                                 collection, parsed_args)

    def take_action_wrapped(self, chunk_size, padding, min_time, collection, parsed_args):
        """Wrapped version of take action"""
        raise NotImplementedError()


class CitoSingleCommand(CitoCommand):
    """CitoSingleCommand base class

    This only looks over some range t0 till t1
    """

    def take_action_wrapped(self, chunk_size, padding, min_time, collection, parsed_args):
        t0 = min_time
        t1 = t0 + chunk_size

        self.log.info('Processing %d %d' % (t0, t1))

        for task in self.get_tasks():
            self.log.debug("Running task", task)
            print(task.process(t0, t1, loops=10))


class CitoContinousCommand(CitoCommand):
    """CitoSingleCommand base class

    This only looks over some range t0 till t1
    """

    def get_tasks(self):
        raise NotImplementedError()

    def get_parser(self, prog_name):
        parser = super(CitoContinousCommand, self).get_parser(prog_name)


        return parser

    def take_action_wrapped(self, chunk_size, padding, min_time, collection, parsed_args):
        current_time_index = int(min_time / chunk_size)
        self.log.debug('Current time index [10 ns]: %d', current_time_index)

        tasks = self.get_tasks(parsed_args)

        start_time = time.time()
        amount_data_processed = 0

        max_time = InputDBInterface.get_max_time(collection)

        # For continous streaming, change ceil -> int
        time_index = math.ceil(max_time / chunk_size)

        self.log.debug("Current min time [10 ns]: %d", min_time)
        self.log.debug("Current max time [10 ns]: %d", max_time)

        self.log.info("Size of data blocks [10 ns]: %d" % chunk_size)

        for i in tqdm(range(current_time_index, time_index)):
            t0 = (i * chunk_size)
            t1 = (i + 1) * chunk_size

            self.log.debug('Processing %d %d' % (t0, t1))

            for task in tasks:
                self.log.debug('Sending data to task: %s',
                              task.__class__.__name__)
                amount_data_processed += task.process(t0, t1)

            dt = (time.time() - start_time)
            data_rate = amount_data_processed / dt
            self.log.debug("%d bytes processed in %d seconds" % (amount_data_processed,
                                                                dt))
            self.log.debug("Rate: %f" % (data_rate / dt))

        self.log.info("Final stats:")
        self.log.info("\t%d bytes processed in %d seconds" % (amount_data_processed,
                                                                dt))
        self.log.info("\tRate: %f" % (data_rate / dt))



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


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
