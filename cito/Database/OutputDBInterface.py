__author__ = 'tunnell'

import logging
import pickle

import snappy

from cito.Database import DBBase


class MongoDBOutput(DBBase.MongoDBBase):

    """Write to MongoDB

    This class, I don't think, can know the event number since it events before it
    may still be being processed.
    """

    def __init__(self, collection_name=None, hostname=DBBase.HOSTNAME):
        DBBase.MongoDBBase.__init__(self, collection_name, hostname)

    @staticmethod
    def get_db_name():
        return 'output'

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
        self.log.debug('writing event')
        mongofied_list = [self.mongify_event(x) for x in event_data_list]

        self.collection.insert(mongofied_list,
                               check_keys=False,
                               manipulate=False,
                               w=0)
