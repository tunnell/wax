"""Interface code to the input data in MongoDB
"""


import logging

import numpy as np

import pymongo
import snappy
from cito.Database import DBBase

__author__ = 'tunnell'


DB_NAME = 'data'
COLLECTION_NAME = 'XENON100'
CONNECTION = None


def get_sort_key(order=pymongo.DESCENDING):
    """Sort key used for MongoDB sorting and indexing.

    :param order: Ascending or descending order.
    :type order: int
    :returns:  list -- Returns, per pymongo format, a list of (variable, order)
                       pairs.


    """
    if order != pymongo.DESCENDING and order != pymongo.ASCENDING:
        raise ValueError()

    return [('triggertime', order),
            ('module', order),
            ('_id', order)]


def get_min_time(collection):
    """Get minimum trigger time in a collection.

    This function is used by the Event Builder to know where to begin building
    events.

    :param collection: A pymongo Collection that will be queried.
    :type collection: pymongo.Collection.
    :returns:  int -- A time in units of 10 ns.
    """
    sort_key = get_sort_key(pymongo.ASCENDING)

    cursor = collection.find({},
                             fields=['triggertime'],
                             limit=1,
                             sort=sort_key)

    doc = next(cursor)
    logging.error('trig time: %s', str(doc))
    time = doc['triggertime']
    if time is None:
        raise ValueError("No time found when searching for minimal time")
    logging.debug("Minimum time: %d", time)
    return time


def get_max_time(collection, min_time=0):
    """Get maximum time that has been seen by all boards.

    Args:
       collection (Collection):  A pymongo Collection that will be queried
       min_time (int): Time that the max must be larger than

    Returns:
       int:  A time in units of 10 ns

    """
    sort_key = get_sort_key()
    modules = collection.distinct('module')

    times = {}

    if not modules:
        raise RuntimeError("No data for any module found")

    for module in modules:
        query = {'module': module,
                 'triggertime': {'$gt': min_time}}

        cursor = collection.find(query,
                                 fields=['triggertime', 'module'],
                                 limit=1,
                                 sort=sort_key)

        # assert(cursor.explain()['indexOnly'])

        times[module] = next(cursor)['triggertime']

    # Want the earliest time (i.e., the min) of all the max times
    # for the boards.
    time = min(times.values())

    return time


def get_data_docs(time0, time1):
    """Fetch from DB the documents within time range.

    .. todo:: Must this know padding?  Maybe just hand cursor so can mock?

    :param time0: Initial time to query.
    :type time0: int.
    :param time1: Final time.
    :type time1: int.
    :returns:  list -- Input documents see docs :ref:`data_format#input`
    :raises: AssertionError
    """
    collection = get_db_connection()[2]

    # $gte and $lt are special mongo functions for greater than and less than
    subset_query = {"triggertime": {'$gte': time0,
                                    '$lt': time1}}

    return list(collection.find(subset_query))


def get_data_from_doc(doc):
    """From a mongo document, fetch the data payload and decompress if
    necessary

    Args:
       doc (dictionary):  Document from mongodb to analyze

    Returns:
       bytes: decompressed data

    """
    data = doc['data']
    assert len(data) != 0

    if doc['zipped']:
        data = snappy.uncompress(data)

    data = np.fromstring(data,
                         dtype=np.uint32)

    if len(data) == 0:
        raise IndexError("Data has zero length")

    return data


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
        logging.warning("Collection %s.%s has no events" %
                        (DB_NAME, COLLECTION_NAME))

    collection.ensure_index(get_sort_key(),
                            background=True)
    CONNECTION = (c, db, collection)
    return CONNECTION