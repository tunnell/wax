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
from cito.cito2 import ureg
import snappy

def get_mongo_db_objects(server='127.0.0.1'):
    """This function returns pymongo objects

    Args:
       server (str):  The server hosting MongoDB.

    Returns:
       [Connection, Database, Collection]

    Raises:
       pymongo.errors.PyMongoError

    """
    c = pymongo.MongoClient(server)
    db = c.data
    collection = db.test
    return c, db, collection

def get_pymongo_collection():
    """Returns a pymongo collection

    Args:
        None

    Returns:
        Collection
    """
    return get_mongo_db_objects()[2]

def get_max_time(collection, order=pymongo.DESCENDING):
    """Get maximum time that has been seen by all boards, unless order is
    changed.

    Args:
       collection (Collection):  A pymongo Collection that will be queried
       order:   Either pymongo.DESCENDING or pymongo.ASDESCENDING.  Useful for
                finding the earliest time (if need be)

    Returns:
       pint.Quantity or None: A time with units set by pint, or None if none found

    """
    sort_key = [('triggertime', order)]
    modules = collection.distinct('module')

    times = {}

    for module in modules:
        query = {'module': module}

        cursor = collection.find(query,
                                 fields=['triggertime'],
                                 limit=1).sort(sort_key)

        times[module] = next(cursor)['triggertime']

    # Want the earliest time (i.e., the min) of all the max times
    # for the boards.
    time = min(times.values())
    return time * ureg.sample

def get_data_from_doc(doc):
    """From a mongo document, fetch the data payload and decompress if
    necessary

    Args:
       doc (dictionary):  Document from mongodb to analyze

    Returns:
       bytes: data

    """
    data = doc['data']
    assert(len(data) != 0)

    if doc['zipped']:
        data = snappy.uncompress(data)

    return data