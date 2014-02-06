__author__ = 'tunnell'

from cito.core import XeDB
from cliff.command import Command
import logging
import tables

import pymongo
import numpy as np
import matplotlib.pyplot as plt
import snappy
import pickle
import gzip

import gzip

class FileBuilderCommand(Command):
    """Continously build files

    TODO: merge with other commands"""

    def get_description(self):
        return self.__doc__

    def get_parser(self, prog_name):
        parser = super(FileBuilderCommand, self).get_parser(prog_name)

        parser.add_argument("--hostname", help="MongoDB database address",
                            type=str,
                            default='127.0.0.1')
        return parser


    def take_action(self, parsed_args):
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.debug('Initialized %s', self.__class__.__name__)
        self.log.debug('Args: %s', str(parsed_args))

        self.log.debug("Getting mongo objects")


        c, db, collection = XeDB.get_mongo_db_objects(selection='output')
        f = gzip.open('testPickleFile.pklz','wb')

        for doc in collection.find():
            doc2 = snappy.uncompress(doc['compressed_doc'])
            doc2 = pickle.loads(doc2)

            pickle.dump(doc2,f)


        f.close()