import pymongo
import numpy as np
import json
import time
from scipy import signal
import block_operations

#if current_channel not in results:
# Samples are actually 14 bit
SAMPLE_TYPE = np.uint16
SAMPLE_TIME_STEP = 1 # units of 10 ns
CHUNK_SIZE =  10**-2 * 10**8 # units of 10 ns, 0.5 s
# 10^-3, 15.82697319984436, 10^-4 0.6667842864990234

def combine_blocks(cursor, offset):
    t00 = time.time()
    t0 = time.time()
    combined_data = np.zeros([CHUNK_SIZE])

    total_data_size = 0
    occurences = []
    i = 0
    for doc in cursor:
        i += 1
        data = doc['data']
        total_data_size += len(data)
        assert(block_operations.get_trigger_time_tag(data) == doc['triggertime'])
        print(doc['module'])
        #print(doc['triggertime'], block_operations.get_trigger_time_tag(data))
        occurences += block_operations.process(data, doc['module'], doc['zipped'],
                                               offset)
    print('i', i)
    print('datasize', total_data_size)
    t1 = time.time()
    print("get_data t1 - t0", t1 - t0)

    t0 = time.time()
    combined_data = np.zeros([1.3*CHUNK_SIZE], dtype = SAMPLE_TYPE)
    result = block_operations.sum_pulses(occurences, combined_data)
    t1 = time.time()
    print("sum t1 - t0", t1 - t0)

    # Need to check bounadries
    t0 = time.time()
    step = 1000
    for k in range(0, i, step):
        print(signal.find_peaks_cwt(combined_data[k:k+step], np.array([100])))
    t1 = time.time()
    print("peaks t1 - t0", t1 - t0)

    t11 = time.time()
    total_data_size = float(total_data_size / 1048576)
    print("Rate:", total_data_size/(t11 - t00))

    import matplotlib.pyplot as plt
    plt.plot(combined_data)
    plt.savefig('output.eps')
    plt.show()
    return i


if __name__ == "__main__":
    c = pymongo.MongoClient()
    db = c.data
    collection = db.test2

    tt = []

    BIG_NUMBER = 100000
    for i in range(BIG_NUMBER):
        query = {'triggertime' : {'$lt' : (i+1) * CHUNK_SIZE, '$gt' : i * CHUNK_SIZE}}

        results = collection.find(query) #, fields={ 'triggertime': 1, 'data':1, 'zipped':1, 'module':1 })
        #print(json.dumps(results.explain(), sort_keys=True, indent=4))
        print('indexOnly', results.explain()['indexOnly'])


        n = combine_blocks(results, offset=(i * CHUNK_SIZE))
        print('n', n)
        if not n:
            break

