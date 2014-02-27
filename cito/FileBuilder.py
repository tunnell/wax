__author__ = 'tunnell'

import logging
import pickle
import gzip

from tqdm import tqdm
from cliff.command import Command
from cito import __version__
import snappy
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
        return parser

    def take_action(self, parsed_args):
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.debug('Initialized %s', self.__class__.__name__)
        self.log.debug('Args: %s', str(parsed_args))

        self.log.debug("Establishing connection")

        c, db, collection = OutputDBInterface.get_db_connection(hostname=parsed_args.hostname)

        cursor = collection.find()
        N = cursor.count()
        if N == 0:
            self.log.error("No events in the output database; no file made.")
            return

        f = gzip.open(parsed_args.filename, 'wb')

        pickle.dump(__version__, f)

        self.log.info("Processing %d trigger events" % N)

        for i in tqdm(range(N)):
            doc = next(cursor)
            doc2 = snappy.uncompress(doc['compressed_doc'])
            doc2 = pickle.loads(doc2)

            pickle.dump(doc2, f)


        f.close()
