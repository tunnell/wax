__author__ = 'tunnell'

import logging
import pickle

import snappy

from cito.core import XeDB


class OutputCommon():
    """Base class for all output
    """

    def __init__(self):
        if 'OutputCommon' == self.__class__.__name__:
            raise ValueError('This is a base class %s',
                             self.__class__.__name__)
        self.log = logging.getLogger(self.__class__.__name__)

    def write_event(self):
        raise NotImplementedError()

    @property
    def event_number(self):
        return "Not set"


class MongoDBOutput(OutputCommon):
    """Write to MongoDB

    This class, I don't think, can know the event number since it events before it
    may still be being processed.
    """

    def __init__(self):
        OutputCommon.__init__(self)

        # MongoDB collection to put data in
        self.conn, self.my_db, self.collection = XeDB.get_mongo_db_objects(selection='output')

    def mongify_event(self, event_data):
        """Convert Python data to pickled and compressed data.

        """
        new_doc = {}
        new_doc['evt_num'] = event_data['evt_num']
        new_doc['range'] = event_data['range']
        data = pickle.dumps(event_data)
        new_doc['compressed_doc'] = snappy.compress(data)

        return new_doc

    def write_events(self, event_data_list):
        """Save data to database
        """
        self.log.debug(event_data_list)
        mongofied_list = [self.mongify_event(x) for x in event_data_list]

        self.collection.insert(mongofied_list)
