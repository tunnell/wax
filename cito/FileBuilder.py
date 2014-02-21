__author__ = 'tunnell'

import logging
import pickle
import gzip

from tqdm import tqdm
from cliff.command import Command
import snappy
from cito.core import XeDB


class FileBuilderCommand(Command):
    """Continously build files


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

        self.log.info("Establishing connection")

        c, db, collection = XeDB.get_mongo_db_objects(parsed_args.hostname,
                                                      selection='output')
        f = gzip.open(parsed_args.filename, 'wb')

        cursor = collection.find()
        N = cursor.count()

        self.log.info("Processing %d trigger events" % N)

        for i in tqdm(range(N)):
            doc = next(cursor)
            doc2 = snappy.uncompress(doc['compressed_doc'])
            doc2 = pickle.loads(doc2)

            pickle.dump(doc2, f)

        f.close()
