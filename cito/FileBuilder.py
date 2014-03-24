from cito.EventBuilder.Processor import sizeof_fmt

__author__ = 'tunnell'

import logging
import pickle
import gzip, lzma, bz2
import time

from tqdm import tqdm
from cliff.command import Command

from cito import __version__
from cito.Database import OutputDBInterface


class FileBuilderCommand(Command):
    """Build files from processed trigger events in output database.


    the output format is Pickled.
    TODO: merge with other commands"""

    def get_description(self):
        return self.__doc__

    def get_parser(self, prog_name):
        parser = super(FileBuilderCommand, self).get_parser(prog_name)

        parser.add_argument("--hostname", help="MongoDB database address",
                            type=str,
                            default='127.0.0.1')
        parser.add_argument("--filename", help="Output filename of pickled data",
                            type=str,
                            default='cito_file.pklz')
        parser.add_argument("--compression", help="Choose compression algorithm (or none)",
                            type=str, default='gzip',
                            choices=['gzip', 'lzma', 'none', 'bz2'])
        return parser

    def take_action(self, parsed_args):
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.debug('Initialized %s', self.__class__.__name__)
        self.log.debug('Args: %s', str(parsed_args))

        self.log.debug("Establishing connection")
        output = OutputDBInterface.MongoDBOutput(hostname=parsed_args.hostname)
        try:
            collection = output.get_collection()
        except RuntimeError:
            self.log.error("Uninitialized (empty? if so, run 'process'.) output database; no file made.")
            return

        t0_read = time.time()
        cursor = collection.find(sort=output.get_sort_key(),
                                 exhaust=True)
        t1_read = time.time()
        N = cursor.count()
        if N == 0:
            self.log.error("No events in the output database; no file made.")
            return

        f = None
        for choice in [bz2, gzip, lzma]:
            name = choice.__name__
            if parsed_args.compression == name:
                f = choice.open(parsed_args.filename + '.' + name, 'wb')

        if f == None:
            f = open(parsed_args.filename, 'wb')


        pickle.dump(__version__, f)

        self.log.info("Processing %d trigger events" % N)

        data_size = 0
        t0_save = time.time()
        for i in tqdm(range(N)):
            doc = next(cursor)
            data_size += doc['size']
            pickle.dump(doc, f)

        t1_save = time.time()
        self.log.debug("Speed: %sps" % sizeof_fmt(data_size/(t1_save-t0_read)))
        self.log.debug("Time: %ds" % (t1_save - t0_read))
        self.log.debug("\tReading-only speed: %sps" % sizeof_fmt(data_size/(t1_read-t0_read)))
        self.log.debug("\tReading-only time: %ds" % (t1_read-t0_read))
        self.log.debug("\tSaving-only speed: %sps" % sizeof_fmt(data_size/(t1_save-t0_save)))
        self.log.debug("\tSaving-only time: %ds" % (t1_save-t0_save))
        self.log.info("Size of uncompressed data: %s " % sizeof_fmt(data_size))

        f.close()
