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
                ("triggertime", pymongo.ASCENDING),
                ('group', pymongo.ASCENDING)]

    # Index for quick query
    collection.create_index(sort_key, dropDups=True)

    last_event = time.time()

    # Loop until Ctrl-C or error
    while (1):
        # This try-except catches Ctrl-C and error
        try:
            # Non-sense query that is in index
            query = {}#{"triggertime": {'$gt': 0}}

            # Perform query
            cursor = collection.find(query,
                                     fields=['triggertime']).sort(sort_key)

            # Are we using index for quick queries?  Not always true if there
            # are no documents in the collection...
            assert(cursor.explain()['indexOnly'] == True)

            # Stats on how the delete worked. Write concern is on.
            result = collection.remove(query)
            print('Deleted %d documents' % result['n'])
            if result['n'] == 0:
                time_diff = (time.time() - last_event)/60

                if time_diff > 60:
                    sleep_time = 5
                if time_diff > 10:
                    sleep_time = 1
                else:
                    sleep_time = 0.1

                print("\tWaiting %0.1f second since no docs... no events since %0.2f minute" % (sleep_time,
                                                                                             time_diff))
                time.sleep(sleep_time)
            else:
                last_event = time.time()

            time.sleep(10)
            if result['err']:
                print(result['err'])
                break

            db.command('repairDatabase')

        except pymongo.errors.OperationFailure as e:
            print('MongoDB error:', e)

        except KeyboardInterrupt:
            print("Ctrl-C caught so exiting.")
            sys.exit(0)
