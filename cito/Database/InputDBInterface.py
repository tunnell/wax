"""Interface code to the input data in MongoDB
"""

import logging

import numpy as np
import pymongo
import snappy

from cito.Database import DBBase

__author__ = 'tunnell'


class MongoDBInput(DBBase.MongoDBBase):
    """Read from MongoDB
    """

    def __init__(self, collection_name=None, hostname=DBBase.HOSTNAME):
        DBBase.MongoDBBase.__init__(self, collection_name, hostname)

        self.control_doc_id = None
        self.is_compressed = None
        self.find_control_doc()

        self.collection.ensure_index(self.get_sort_key(),
                                     background=True)


    @staticmethod
    def get_db_name():
        return 'input'

    def find_control_doc(self):
        control_docs = list(self.collection.find({"runtype": {'$exists': True},
                                                  "latesttime": {'$exists': True},
                                                  "starttime": {'$exists': True},
                                                  "compressed": {'$exists': True},
                                                  "data": {'$exists': False}}))

        if len(control_docs) > 1:
            raise RuntimeError("More than one control document found")
        if len(control_docs) == 0:
            raise RuntimeError("No control document found")
        if self.control_doc_id is not None:
            raise RuntimeError("Control document already set")
        self.control_doc_id = control_docs[0]['_id']
        logging.info("Control document:")
        for key, value in control_docs[0].items():
            logging.info('\t%s: %s' % (key, value))

        self.is_compressed = control_docs[0]['compressed']


    def get_max_time(self):
        """Get maximum time that has been seen by any channel.

        Returns:
           int:  A time in units of 10 ns

        """
        return self.collection.find_one({'_id': self.control_doc_id})['latesttime']

    def get_min_time(self):
        """Get minumum time

        Returns:
           int:  A time in units of 10 ns

        """
        return self.collection.find_one({'_id': self.control_doc_id})['starttime']


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