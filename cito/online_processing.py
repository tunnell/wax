"""Online processing executable
"""

__author__ = 'tunnell'
import pymongo
from cito.cito2 import ureg
from cito import db
import sys
import time




def get_only_old_blocks():
    """Determine which groups are old
    """
    pass


def delete_docs(collection, cursor):
    return


def process(collection, func, t0, t1):
    t0 = t0.to('sample')
    t1 = t1.to('sample')

    # $gte and $lt are special mongo functions for greater than and less than
    subset_query = {"triggertime": {'$gte': t0.magnitude,
                                    '$lt': t1.magnitude}}
    cursor = collection.find(subset_query, )
    count = cursor.count()
    t0.to('s')
    t1.to('s')
    if count:
        print('\tRange:', t0, t1, 'with %d docs' % cursor.count())
    #cursor = collection.find(subset_query,
    #                         fields=['triggertime', 'module'])
    func(collection, cursor)

    collection.remove(subset_query)

if __name__ == "__main__":

    chunk_size = 1 * ureg['sec']
    # When deleting, delete padding behind you in time?
    padding = 1 * ureg['microsecond']

    conn, my_db, collection = db.get_mongo_db_objects()

    # Key to sort by so we can use an index for quick query
    sort_key = [
        ('triggertime', pymongo.DESCENDING),
    ]

    # Index for quick query

    collection.create_index(sort_key, dropDups=True)
    current_time_index = 0

    # Loop until Ctrl-C or error
    while (1):
        # This try-except catches Ctrl-C and error
        try:
            # Non-sense query that is in index
            query = {"triggertime": {'$gt': 0}}

            max_time = db.get_max_time(collection)
            time_index = max_time / chunk_size.to('sample')
            time_index = int(time_index.magnitude)

            #print('up to', max_time.to('s'), current_time_index * chunk_size)
            if time_index > current_time_index:
                start_time = time.time()
                diff = time_index-current_time_index
                #print(current_time_index, 'current time', time_index, 'newtime', diff, 'diff')
                for i in range(current_time_index, time_index):
                    process(collection, delete_docs, i *
                            chunk_size - padding, (i + 1) * chunk_size)

                end_time = time.time()
                print('Time for', diff, 'groups', (end_time - start_time)/diff)
                current_time_index = time_index
                #my_db.command('repairDatabase')

        except StopIteration:
            pass
        except ValueError as e:
            #print("ValueError:", e)
            pass # This means no events left
        except pymongo.errors.OperationFailure as e:
            print('MongoDB error:', e)
        except KeyboardInterrupt:
            print("Ctrl-C caught so exiting.")
            sys.exit(0)
