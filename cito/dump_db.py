"""Delete all documents every second forever"""

__author__ = 'tunnell'

import sys
import time
import json

import pymongo


if __name__ == "__main__":
    c = pymongo.MongoClient()

    db = c.data
    collection = db.test

    # Key to sort by so we can use an index for quick query
    sort_key = [("_id", pymongo.ASCENDING),
                ("triggertime", pymongo.ASCENDING)]

    # Index for quick query
    collection.create_index(sort_key, dropDups=True)

    # Loop until Ctrl-C or error
    while (1):
        # This try-except catches Ctrl-C and error
        try:
            # Non-sense query that is in index
            query = {"triggertime": {'$gt': 0}}

            # Perform query
            cursor = collection.find(query,
                                     fields=['triggertime']).sort(sort_key)

            # Are we using index for quick queries?  Not always true if there
            # are no documents in the collection...
            print('Using index:', cursor.explain()['indexOnly'])

            # Stats on how the delete worked. Write concern is on.
            print(json.dumps(collection.remove(query),
                             indent=4,
                             sort_keys=True))

            # Wait a second so we don't query the DB too much
            time.sleep(1)

        except pymongo.errors.OperationFailure as e:
            print('MongoDB error:', e)

        except KeyboardInterrupt:
            print("Ctrl-C caught so exiting.")
            sys.exit(0)
