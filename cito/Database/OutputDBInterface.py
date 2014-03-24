__author__ = 'tunnell'

import pymongo

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

    @staticmethod
    def get_sort_key():
        """Sort key used for MongoDB sorting and indexing.

        :param order: Ascending or descending order.
        :type order: int
        :returns:  list -- Returns, per pymongo format, a list of (variable, order)
                           pairs.
        """
        return [('cnt', pymongo.ASCENDING), ('_id', pymongo.ASCENDING)]

    def write_events(self, event_data_list):
        """Save data to database
        """
        self.log.debug('writing event')
        #mongofied_list = [self.mongify_event(x) for x in event_data_list]

        self.collection.insert(event_data_list,
                               check_keys=False,
                               manipulate=False,
                               w=0)
