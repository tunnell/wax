# cito - The Xenon1T experiments software trigger
# Copyright 2013.  All rights reserved.
# https://github.com/tunnell/cito
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following disclaimer
# in the documentation and/or other materials provided with the
# distribution.
#     * Neither the name of the Xenon experiment, nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""Interface and schema for DB access
"""

__author__ = 'tunnell'

import pymongo
import snappy
import logging

def get_server_name():
    return '127.0.0.1'

def get_mongo_db_objects(server=get_server_name()):
    """This function returns pymongo objects

    Args:
       server (str):  The server IP or DNS name MongoDB.

    Returns:
       [Connection, Database, Collection]

    Raises:
       pymongo.errors.PyMongoError

    """
    db_name = 'data'
    collection_name = 'pulses'

    c = pymongo.MongoClient(server)

    db = c[db_name]
    collection = db[collection_name]

    num_docs_in_collection = collection.count()
    if num_docs_in_collection == 0:
        raise RuntimeError("Collection %s.%s contains no events; can't continue" % (db_name, collection_name))

    collection.ensure_index(get_sort_key(),
                            background=True)

    # Used for module list finding. TODO: This do anything?
    collection.ensure_index([('module', pymongo.DESCENDING)],
                            background=True)

    return c, db, collection


def get_pymongo_collection():
    """Returns the current pymongo collection.

    Args:
        None

    Returns:
        Collection
    """
    return get_mongo_db_objects()[2]


def get_sort_key():
    """Sort key used for MongoDB sorting and indexing.

    Args:
       None

    Returns:
       list:  Returns, per pymongo format, a list of (variable, order) pairs.

    """
    return [('triggertime', pymongo.DESCENDING),
            ('module', pymongo.DESCENDING),
            ('_id', pymongo.DESCENDING)]


def get_min_time(collection):
    """Get minimum time in collection.

    Args:
       collection (Collection):  A pymongo Collection that will be queried

    Returns:
       int:  A time in units of 10 ns

    """
    sort_key = get_sort_key()
    sort_key = [(x[0], pymongo.ASCENDING) for x in sort_key]

    cursor = collection.find({},
                             fields=['triggertime'],
                             limit=1,
                             sort=sort_key)
    time = next(cursor)['triggertime']
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


def get_data_from_doc(doc):
    """From a mongo document, fetch the data payload and decompress if
    necessary

    Args:
       doc (dictionary):  Document from mongodb to analyze

    Returns:
       bytes: decompressed data

    """
    data = doc['data']
    assert (len(data) != 0)

    if doc['zipped']:
        data = snappy.uncompress(data)

    return data
