"""Interface code to the input data in MongoDB
"""

import logging

import numpy as np
import pymongo
import snappy

from wax.Database import DBMongoBase

__author__ = 'tunnell'


class MongoDBInput(DBMongoBase.MongoDBBase):

    """Read from MongoDB
    """

    def __init__(self, collection_name=None, hostname=DBMongoBase.HOSTNAME):
        self.control_doc_id = None
        self.is_compressed = None

        DBMongoBase.MongoDBBase.__init__(self, collection_name, hostname)

        if self.initialized is False:
            self.log.debug("Cannot initialize input.")
            return

        self.find_control_doc()

        self.collection.ensure_index(self.get_sort_key(),
                                     background=True)

    @staticmethod
    def get_db_name():
        return 'input'

    def find_control_doc(self):
        control_docs = list(self.collection.find({"runtype": {'$exists': True},
                                                  "starttime": {'$exists': True},
                                                  "compressed": {'$exists': True},
                                                  "data_taking_ended": {'$exists': True},
                                                  "data": {'$exists': False}}))

        if len(control_docs) > 1:
            raise RuntimeError("More than one control document found in %s." %
                               self.get_collection_name())
        elif self.control_doc_id is not None:
            raise RuntimeError("Control document already set")
        elif len(control_docs) == 0:
            self.log.error("No control document found.")
            self.initialized = False
            return

        self.control_doc_id = control_docs[0]['_id']
        logging.info("Control document:")
        for key, value in control_docs[0].items():
            logging.info('\t%s: %s' % (key, value))

        self.is_compressed = control_docs[0]['compressed']

    def get_control_document(self):
        """Fetch current control document from collection

        This stores all the information about the dataset

        :returns:  dict -- Control document.
        """
        return self.collection.find_one({'_id': self.control_doc_id})

    def get_modules(self):
        """Get modules

        :returns:  list[int] -- Return list of integers

        """
        modules = self.collection.distinct('module')
        if len(modules) == 0:
            raise RuntimeError("No modules found")
        return [x for x in modules if x is not None]

    def get_max_time(self):
        """Get maximum time that has been seen by any channel.

        :returns:  int -- A time in units of 10 ns

        """
        sort_key = self.get_sort_key()

        if self.has_run_ended():
            doc = self.collection.find_one({},
                                           fields=['time'],
                                           sort=sort_key)
            if doc is None or doc['time'] is None:
                return self.get_min_time()
            return doc['time']

        modules = self.get_modules()
        times = {}

        for module in modules:
            query = {'module': module}
            doc = self.collection.find_one(query,
                                           fields=['time', 'module'],
                                           limit=1,
                                           sort=sort_key)

            if doc is None:
                return self.get_min_time()
            # See if cursor is fast with cursor.explain()['indexOnly']

            times[module] = doc['time']

        # Want the earliest time (i.e., the min) of all the max times
        # for the boards.
        if len(list(times.values())) == 0:
            return self.get_min_time()
        time = min(times.values())

        return time

    def get_min_time(self):
        """Get minumum time

        Returns:
           int:  A time in units of 10 ns

        """
        sort_key = self.get_sort_key(pymongo.ASCENDING)
        doc = self.collection.find_one({"time": {'$exists': True}},
                                       sort=sort_key)
        if doc == None:
            raise ValueError("Could not find starting time since no documents with 'time' field exist")
        return doc['time']
        # return self.get_control_document()['starttime']

    def has_run_ended(self):
        """Determine if run has ended

        Returns:
           int:  A time in units of 10 ns

        """
        return self.get_control_document()['data_taking_ended']

    def get_data_docs(self, time0, time1):
        """Fetch from DB the documents within time range.

        .. todo:: Must this know padding?  Maybe just hand cursor so can mock?

        :param time0: Initial time to query.
        :type time0: int.
        :param time1: Final time.
        :type time1: int.
        :returns:  list -- Input documents see docs :ref:`data_format#input`
        :raises: AssertionError
        """

        # $gte and $lt are special mongo functions for greater than and less than
        subset_query = {"time": {'$gte': time0,
                                 '$lt': time1}}

        result = list(self.collection.find(subset_query))
        logging.debug("Fetched %d input documents." % len(result))
        return result

    @staticmethod
    def get_sort_key(order=pymongo.DESCENDING):
        """Sort key used for MongoDB sorting and indexing.

        :param order: Ascending or descending order.
        :type order: int
        :returns:  list -- Returns, per pymongo format, a list of (variable, order)
                           pairs.


        """
        if order != pymongo.DESCENDING and order != pymongo.ASCENDING:
            raise ValueError()

        return [('time', order),
                ('module', order),
                ('_id', order)]

    def get_data_from_doc(self, doc):
        """From a mongo document, fetch the data payload and decompress if
        necessary

        Args:
           doc (dictionary):  Document from mongodb to analyze

        Returns:
           bytes: decompressed data

        """
        data = doc['data']
        assert len(data) != 0

        if self.is_compressed:
            data = snappy.uncompress(data)

        data = np.fromstring(data,
                             dtype=np.uint32)

        if len(data) == 0:
            raise IndexError("Data has zero length")

        return data
