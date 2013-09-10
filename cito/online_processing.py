__author__ = 'tunnell'
import pymongo
from cito import ureg


def get_default_collection():
    c = pymongo.MongoClient()
    db = c.data
    collection = db.test
    return collection

def get_only_old_blocks():
    """Determine which groups are old
    """
    pass

def delete_docs(collection, cursor):
    print(cursor.count())


def process(collection, func, t0, t1):
    print('\t', t0, t1)
    t0 = t0.to('sample')
    t1 = t1.to('sample')
    query = {"triggertime": {'$ge': t0.magnitude, '$lt': t1.magnitude}}


    cursor = collection.find(query,
                             fields=['triggertime'])
    func(collection, cursor)

    collection.remove(query)

def get_max_time(collection):
    """Get maximum time that has been seen by all boards

    :param collection: A pyMongo collection
    :return: max time
    """
    sort_key = [('triggertime', pymongo.DESCENDING)]
    modules = collection.distinct('module')

    times = {}

    for module in modules:
        query = {'module' : module}

        cursor = collection.find(query,
                                 fields=['triggertime'],
                                 limit=1).sort(sort_key)

        time = next(cursor)
        time = time['triggertime']
        time = time & 0xFFFFFFFF
        times[module] = time

    # Want the earliest time (i.e., the min) of all the max times
    # for the boards.
    max_time = min(times.values())
    print(times, max_time)
    return max_time * ureg.sample


if __name__ == "__main__":
    chunk_size = 1 * ureg['sec']
    padding = 1 * ureg['microsecond']  # When deleting, delete padding behind you in time?

    collection = get_default_collection()

    # Key to sort by so we can use an index for quick query
    sort_key =  [
                          ('triggertime', pymongo.DESCENDING),
                          ]

    # Index for quick query

    collection.create_index(sort_key, dropDups=True)

    current_time_index = 44087

    # Loop until Ctrl-C or error
    while (1):
        # This try-except catches Ctrl-C and error
        try:
            # Non-sense query that is in index
            query = {"triggertime": {'$gt': 0}}

            max_time = get_max_time(collection)
            time_index = max_time / chunk_size.to('sample')
            time_index = int(time_index.magnitude)

            print('up to', max_time.to('s'), current_time_index * chunk_size)
            for i in range(current_time_index, time_index):
                process(collection, delete_docs, i*chunk_size - padding, (i+1) * chunk_size)

            current_time_index = time_index

        except StopIteration:
            pass
        except pymongo.errors.OperationFailure as e:
            print('MongoDB error:', e)
        except KeyboardInterrupt:
            print("Ctrl-C caught so exiting.")
            sys.exit(0)


