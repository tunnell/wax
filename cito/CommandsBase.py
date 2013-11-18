"""Base classes

Include inspector in this"""

__author__ = 'tunnell'

import logging
import time
import sys

from cliff.command import Command
from cliff.show import ShowOne
import pymongo

from cito.core import XeDB


class CitoCommand(Command):
    """CitoSingleCommand base class

    This only looks over some range t0 till t1
    """

    # Key to sort by so we can use an index for quick query
    sort_key = [
        ('triggertime', pymongo.DESCENDING),
        ('module', pymongo.DESCENDING)
    ]

    # def __init__(self):
    # Command.__init__(self)
    #    log = logging.getLogger(__name__)

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

        self.log.debug("take_action_wrapped")

        self.log.debug("Getting mongo objects")
        conn, my_db, collection = XeDB.get_mongo_db_objects(
            parsed_args.hostname)

        # Index for quick query
        self.log.debug("Creating index")
        collection.create_index(self.sort_key, dropDups=True)

        min_time = XeDB.get_min_time(collection)

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

        parser.add_argument('-n', '--numevents', type=int,
                               help='Number of events to process')

        return parser

    def take_action_wrapped(self, chunk_size, padding, min_time, collection, parsed_args):
        current_time_index = int(min_time / chunk_size)
        self.log.debug('Current time index %d', current_time_index)

        tasks = self.get_tasks()

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

                        self.log.info('Processing %d %d' % (t0, t1))

                        for task in tasks:
                            if i > parsed_args.numevents:
                                raise StopIteration
                            self.log.info('Sending data to task: %s',
                                          task.__class__.__name__)
                            task.process(t0, t1)

                    current_time_index = time_index
                else:
                    self.log.debug('Waiting %f seconds' % parsed_args.waittime)
                    time.sleep(parsed_args.waittime)
                    # my_db.command('repairDatabase')
                    # break
            except StopIteration:
                pass
            except ValueError as e:
                self.log.exception(e)
                raise  # pass # This means no events left
            except KeyboardInterrupt:
                self.log.info("Ctrl-C caught so exiting.")
                sys.exit(0)


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
