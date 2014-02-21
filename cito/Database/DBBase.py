"""Base class for all DB operationsInterface and schema for DB access
"""
from cito.Database.InputDBInterface import get_sort_key

__author__ = 'tunnell'

import pymongo

CONNECTIONS = {}
HOSTNAME = "127.0.0.1"

def get_db_connection(selection='input',
                      hostname=HOSTNAME):
    """Get database connection objects for the input or output databases.

    This function creates MongoDB connections to either the input or output
    databases.  It also maintains a cache of connections that have already been
    created to speed things up.

    :param hostname: The IP or DNS name where MongoDB is hosted on port 27017
    :type hostname: str.
    :param selection: 'input' for EventBuilder input,  blocks, otherwise 'output' for output
    :type selection: str.
    :returns:  list -- [pymongo.Connection, pymongo.Database, pymongo.Collection]
    :raises: pymongo.errors.PyMongoError
    """
    # Check if in cache
    if selection in CONNECTIONS.keys():
        return CONNECTIONS[selection]

    # Locations within MongoDB of database and collection.
    # Todo: The names of databases should really be a variable.  So should hostname.
    if selection == 'input':
        db_name = 'data'
        collection_name = 'XENON100'  # todo: config?
    elif selection == 'output':
        db_name = 'output'
        collection_name = 'somerun'
    else:
        raise ValueError()

    # If not in cache, make new connection, db, and collection objects
    c = pymongo.MongoClient(hostname)
    db = c[db_name]
    collection = db[collection_name]

    # For the input database, we also want to create some indices to speed up
    # queries.
    if selection == 'input':
        num_docs_in_collection = collection.count()
        if num_docs_in_collection == 0:
            raise RuntimeError("Collection %s.%s has no events" %
                               (db_name, collection_name))

        collection.ensure_index(get_sort_key(),
                                background=True)
    CONNECTIONS[selection] = (c, db, collection)
    return c, db, collection







