"""Base class for all DB interfaces.

This class provides various functions for creating connections to MongoDB and
also locating the MongoDB server.
"""

import logging

import pymongo

from wax.Configuration import HOSTNAME

CONNECTION = None


class MongoDBBase():

    """Read from MongoDB

    The subclass is responsible for setting up the collection
    """

    def __init__(self, collection_name=None, hostname=HOSTNAME):
        self.log = logging.getLogger(self.__class__.__name__)

        global CONNECTION
        if CONNECTION is None:
            self.log.debug("Creating first pymongo connection.")
            CONNECTION = pymongo.Connection(hostname)
        else:
            self.log.debug("Reusing old pymongo connection.")

        self.db = CONNECTION[self.get_db_name()]

        self.initialized = True

        if collection_name is not None:
            self.collection = self.db[collection_name]
        else:
            self.collection = self.discover_collection()

        self.hostname = hostname

    @staticmethod
    def get_db_name():
        raise NotImplementedError()

    @staticmethod
    def get_sort_key():
        raise NotImplementedError()

    def discover_collection(self):
        collections = self.db.collection_names(include_system_collections=False)
        if len(collections) == 0:
            self.log.warning("No dataset in %s database." % self.get_db_name())
            self.initialized = False
            return

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
            raise RuntimeError("Empty collection.")
        else:
            logging.info("Collection %s.%s has %d documents" %
                         (self.get_db_name(), collection_name, num_docs_in_collection))

        return self.collection

    def get_collection(self):
        if not self.initialized:
            raise RuntimeError("Not initialized.")
        elif self.collection is None:
            raise ValueError("No collection present.")
        return self.collection

    def get_db(self):
        if not self.initialized or self.db is None:
            raise ValueError
        return self.db

    def get_collection_name(self):
        return self.get_collection().name

    def get_hostname(self):
        return self.hostname
