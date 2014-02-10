import logging
import logging.config
import os
import sys
import time

from cliff.app import App
from cliff.command import Command
from cliff.commandmanager import CommandManager
from cliff.show import ShowOne

import cito
from cito.core import __all__


class CitoApp(App):
    """Cito Cliff application

    See cliff documentation to understand this."""

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
                            default=2 ** 17)
        parser.add_argument('--padding', type=int,
                            help='Padding to overlap processing windows [10 ns step]',
                            default=10 ** 2)

        return parser

    def get_tasks(self):
        raise NotImplementedError()

    def take_action(self, parsed_args):
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.debug('Initialized %s', self.__class__.__name__)

        self.log.debug("take_action")
        chunk_size = parsed_args.chunksize
        padding = parsed_args.padding

        self.log.debug('Args: %s', str(parsed_args))

        self.log.debug("Getting mongo objects")
        conn, my_db, collection = XeDB.get_mongo_db_objects(selection='input',
                                                            server=parsed_args.hostname)
        self.log.error(collection.count())
        min_time = XeDB.get_min_time(collection)

        self.log.debug("take_action_wrapped")
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

        parser.add_argument('-n', '--num', type=int, default=-1,
                            help='Number of time chunks to process')
        parser.add_argument('-w', '--waittime', type=int, default=-1,
                            help='Time to wait (negative means do not)')

        return parser

    def take_action_wrapped(self, chunk_size, padding, min_time, collection, parsed_args):
        current_time_index = int(min_time / chunk_size)
        self.log.debug('Current time index %d', current_time_index)

        tasks = self.get_tasks()

        start_time = time.time()
        amount_data_processed = 0

        # Loop until Ctrl-C or error
        while (1):
            self.log.debug("Entering while loop; use Ctrl-C to exit")

            try:
                max_time = XeDB.get_max_time(collection)
                time_index = int(max_time / chunk_size)

                self.log.debug("Current max time: %d", max_time)

                if time_index > current_time_index:
                    for i in range(current_time_index, time_index):
                        t0 = (i * chunk_size)
                        t1 = (i + 1) * chunk_size

                        # Break if enough processed, simulate KeyboardInterrupt
                        # for testing
                        if parsed_args.num != -1:
                            self.log.debug(
                                '%d %d', i, (int(min_time / chunk_size) + parsed_args.num))
                            if i > (int(min_time / chunk_size) + parsed_args.num):
                                self.log.info("Reached maximum number of docs, exiting...")
                                raise KeyboardInterrupt

                        self.log.info('Processing %d %d' % (t0, t1))

                        for task in tasks:
                            self.log.info('Sending data to task: %s',
                                          task.__class__.__name__)
                            amount_data_processed += task.process(t0, t1)

                        dt = (time.time() - start_time)
                        data_rate = amount_data_processed / dt
                        self.log.info("%d bytes processed in %d seconds" % (amount_data_processed,
                                                                            dt))
                        self.log.info("Rate: %f" % (data_rate / dt))

                    current_time_index = time_index
                else:
                    if parsed_args.waittime < 0:
                        break
                    self.log.debug('Waiting %f seconds' % parsed_args.waittime)
                    time.sleep(parsed_args.waittime)
                    # my_db.command('repairDatabase')
                    # break
            except StopIteration:
                raise  # pass
            except KeyboardInterrupt:
                self.log.info("Ctrl-C caught so exiting.")
                break


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
