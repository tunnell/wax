__author__ = 'tunnell'

import logging
import pickle
from cito.Database import DBBase
import snappy
import pymongo

DB_NAME = 'output'
COLLECTION_NAME = 'somerun'
CONNECTION = None

def get_db_connection(hostname=DBBase.HOSTNAME):
    """Get database connection objects for the input or output databases.

    This function creates MongoDB connections to either the input or output
    databases.  It also maintains a cache of connections that have already been
    created to speed things up.

    :param hostname: The IP or DNS name where MongoDB is hosted on port 27017
    :type hostname: str.
    :param selection: 'input' for EventBuilder input,  blocks, otherwise
                      'output' for output
    :type selection: str.
    :returns:  list -- [pymongo.Connection,
                        pymongo.Database,
                        pymongo.Collection]
    :raises: pymongo.errors.PyMongoError
    """
    # Check if in cache
    global CONNECTION
    if CONNECTION is not None:
        return CONNECTION


    # If not in cache, make new connection, db, and collection objects
    c = pymongo.MongoClient(hostname)
    db = c[DB_NAME]
    collection = db[COLLECTION_NAME]

    # For the input database, we also want to create some indices to speed up
    # queries.
    num_docs_in_collection = collection.count()
    if num_docs_in_collection == 0:
        logging.debug("Output collection %s.%s is empty" %
                      (DB_NAME, COLLECTION_NAME))
    else:
        logging.warning("Output collection %s.%s has %d; will append data." %
                        (DB_NAME, COLLECTION_NAME, num_docs_in_collection))

    CONNECTION = (c, db, collection)
    return CONNECTION

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

    def __init__(self, hostname='127.0.0.1'):
        OutputCommon.__init__(self)

        # MongoDB collection to put data in
        self.conn, self.my_db, self.collection = get_db_connection(hostname=hostname)


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

