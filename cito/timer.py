__author__ = 'tunnell'

import pymongo
import numpy as np
import json
import time
import cito.combine_blocks
import cito.InterfaceV1724 as bo


def connect_and_run(f, size_parm = None):
    c = pymongo.MongoClient()
    db =    c.data
    collection = db.test

    timer_start = time.time()

    if size_parm == None:
        size = 0
    else:
        size = size_parm

    BIG_NUMBER = 1
    for i in range(BIG_NUMBER):
        t0 = i * combine_blocks.CHUNK_SIZE
        t1 = (i+1) * combine_blocks.CHUNK_SIZE
        query = {'triggertime' : {'$lt' : t1, '$gt' : t0}, 'group': 1}

        results = collection.find(query)

        retval = f(results, offset=(i * combine_blocks.CHUNK_SIZE))

        if size_parm == None:
            size += retval


    dt = time.time() - timer_start
    print("\tTime:", dt, 's')
    print("\tRate:", float(size)/(dt * 1048576), 'MB/s')
    print("\tSize:", float(size)/1048576, 'MB')

    return size

def get_size(results, offset ):
    size = 0
    for result in results:
        size += len(result['data'])

    return size

if __name__ == "__main__":
    print("Do Nothing")
    size = connect_and_run(get_size, None)

    print("Get occurences")
    connect_and_run(combine_blocks.get_occurences, size)

    print("Combine")
    connect_and_run(combine_blocks.combine_blocks, size)

    print("Profiling")

    import cProfile, pstats, io
    pr = cProfile.Profile()
    pr.enable()
    connect_and_run(combine_blocks.combine_blocks, size)
    pr.disable()
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s)
    ps.sort_stats('cumulative')
    ps.print_stats()
    s.seek(0)
    print(s.read())

