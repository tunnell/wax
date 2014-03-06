"""Base class for all DB interfaces.

This class provides various functions for creating connections to MongoDB and
also locating the MongoDB server.
"""

import logging

import pymongo


HOSTNAME = "127.0.0.1"


class MongoDBBase():
    """Read from MongoDB

    The subclass is responsible for setting up the collection
    """

    def __init__(self, collection_name=None, hostname=HOSTNAME):
        self.log = logging.getLogger(self.__class__.__name__)
        self.connection = pymongo.MongoClient(hostname)
        self.db = self.connection[self.get_db_name()]

        if collection_name is not None:
            self.collection = self.db[collection_name]
        else:
            self.collection = self.discover_collection()


    @staticmethod
    def get_db_name():
        raise NotImplementedError()

    def discover_collection(self):
        collections = self.db.collection_names(include_system_collections=False)
        if len(collections) == 0:
            raise RuntimeError("No dataset in %s database." % self.get_db_name())

        if len(collections) > 1:
            logging.warning("Multiple collections found:")
            for collection_name in collections:
                logging.warning("\t%s" % collection_name)

        collection_name = collections[0]
        logging.info("Using collection: %s" % collection_name)
        self.collection = self.db[collection_name]

        # For the input database, we also want to create some indices to speed up
        # queries.
        num_docs_in_collection = self.collection.count()
        if num_docs_in_collection == 0:
            logging.fatal("Collection %s.%s is empty" %
                          (self.get_db_name(), collection_name))
        else:
            logging.info("Collection %s.%s has %d documents" %
                         (self.get_db_name(), collection_name, num_docs_in_collection))

        return self.collection


    def get_collection(self):
        if self.collection == None:
            raise ValueError
        return self.collection

    def get_db(self):
        if self.db == None:
            raise ValueError
        return self.db

    def get_collection_name(self):
        return self.get_collection().name