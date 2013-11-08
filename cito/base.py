"""Base classes

Include inspector in this"""

__author__ = 'tunnell'


from cliff.command import Command
import logging
import time
from cito.helpers import xedb
import pymongo
from cliff.show import ShowOne
from cito.helpers import tasks, xedb
import sys

class CitoCommand(Command):
    """CitoSingleCommand base class

    This only looks over some range t0 till t1
    """

    log = logging.getLogger(__name__)
    # Key to sort by so we can use an index for quick query
    sort_key = [
            ('triggertime', pymongo.DESCENDING),
            ('module', pymongo.DESCENDING)
        ]

    def get_description(self):
        return self.__doc__

    def get_parser(self, prog_name):
        self.log.debug("Setting up parser")
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
        self.log.debug("Parser setup")

        return parser

    def get_tasks(self):
        raise NotImplementedError()


    def take_action(self, parsed_args):
        self.log.debug("take_action")
        chunk_size = parsed_args.chunksize
        padding = parsed_args.padding

        self.log.debug("take_action_wrapped")

        self.log.debug("Getting mongo objects")
        conn, my_db, collection = xedb.get_mongo_db_objects(
            parsed_args.hostname)

        # Index for quick query
        self.log.debug("Creating index")
        collection.create_index(self.sort_key, dropDups=True)

        min_time = xedb.get_min_time(collection)

        self.take_action_wrapped(chunk_size, padding, min_time, collection, parsed_args)

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
    def get_parser(self, prog_name):
        self.log.debug("Setting up parser")
        parser = super(CitoContinousCommand, self).get_parser(prog_name)

        self.log.debug("Parser setup")

        return parser

    def take_action_wrapped(self, chunk_size, padding, min_time, collection, parsed_args):
        current_time_index = int(min_time / chunk_size)
        self.log.debug('Current time index %d', current_time_index)

        # Loop until Ctrl-C or error
        while (1):
            # This try-except catches Ctrl-C and error
            try:
                max_time = xedb.get_max_time(collection)
                time_index = int(max_time / chunk_size)

                self.log.debug('Previous chunk %d' % current_time_index)
                self.log.debug('Current chunk %d' % time_index)
                if time_index > current_time_index:
                    for i in range(current_time_index, time_index):
                        t0 = (i * chunk_size - padding)
                        t1 = (i + 1) * chunk_size
                        self.log.info('Processing %d %d' % (t0, t1))

                        for task in self.get_tasks():
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


class TimingTask():
    def process(self, t0, t1, loops=1, verbose=False):
        sums = 0.0
        mins = 1.7976931348623157e+308
        maxs = 0.0
        print('====%s Timing====' % self.__class__.__name__)
        for i in range(0, loops):
            start_time = time.time()
            result = self.call(t0, t1)
            dt = time.time() - start_time
            mins = dt if dt < mins else mins
            maxs = dt if dt > maxs else maxs
            sums += dt
            if verbose == True:
                print('\t%r ran in %2.9f sec on run %s' %
                      (self.__class__.__name__, dt, i))
        print('%r min run time was %2.9f sec' %
              (self.__class__.__name__, mins))
        print('%r max run time was %2.9f sec' %
              (self.__class__.__name__, maxs))
        print('%r avg run time was %2.9f sec in %s runs' %
              (self.__class__.__name__, sums / loops, loops))

        size = result / 1024
        print('%r size %d kB %s runs' % (self.__class__.__name__, size, loops))
        size = size / 1024  # MB
        print('%r size %d MB %s runs' % (self.__class__.__name__, size, loops))
        speed = size / (sums / loops)
        print('%r avg speed %2.9f MB/s in %s runs' %
              (self.__class__.__name__, speed, loops))
        print('==== end ====')
        return result

    def get_cursor(self, t0, t1):
        conn, mongo_db_obj, collection = xedb.get_mongo_db_objects()

        # $gte and $lt are special mongo functions for greater than and less than
        subset_query = {"triggertime": {'$gte': t0,
                                        '$lt': t1}}
        return collection.find(subset_query)

    def call(self, t0, t1):
        raise NotImplementedError()
