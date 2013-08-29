import pymongo
import numpy as np
import json
import time
from scipy import signal
import block_operations as bo

# TODO: some of this stuff should really be broken out into a Caen Python API.

#if current_channel not in results:
# Samples are actually 14 bit
SAMPLE_TYPE = np.uint16
SAMPLE_TIME_STEP = 1 # units of 10 ns
CHUNK_SIZE =    10**8 # units of 10 ns, 0.5 s
# 10^-3, 15.82697319984436, 10^-4 0.6667842864990234

def check_document_sanity(doc):
    data = doc['data']
    assert(len(data) != 0)
    assert(bo.get_trigger_time_tag(data) == doc['triggertime'])
    bo.check_header(data)

def get_occurences(cursor, offset):
    occurences = []

    for doc in cursor:
        #print(doc)
        check_document_sanity(doc)
        data = doc['data']
        occurences += bo.process(data, doc['module'], doc['zipped'],
                                               offset)
    return occurences


def get_bins(peaks):
    status = np.zeros([1.3*CHUNK_SIZE], dtype = np.dtype(bool))

    for peak in peaks:
        for i in range(peak - 1000, peak + 1000):
            status[i] = True

    peaks.sort()
    bins = [-2**32]
    last_value = 0
    for i in range(status.size):
        if status[i] != last_value:
            bins.append(i)
            last_value = status[i]
    bins += [2**32]
    bins = np.array(bins)
    return bins

def determine_data_to_store(occurences, peaks):
    new_occurences = []

    bins = get_bins(peaks)

    stats = {'saved': 0, 'not_saved' : 0}
    print(bins)

    for occurence in occurences:
        # Instead of adjusting every sample, we just adjust the bin locations
        #bins -= occurence['time_start']
        x = [(occurence['time_start'] + i) for i in range(len(occurence['samples']))]
        y = occurence['samples']
        assert(len(x) == len(y))

        new_occurence = None

        inds = np.digitize(x, bins)
        for n in range(len(x)):
            must_save = ((inds[n]-1) % 2 == 1)
            #print(must_save)

            if must_save and new_occurence == None:
                new_occurence = {}
                new_occurence['channel'] = occurence['channel']
                new_occurence['module'] = occurence['module']
                new_occurence['time_start'] = x[n]
                new_occurence['samples'] = []

            if must_save:
                new_occurence['samples'].append(y[n])
                stats['saved'] += 1
            else:
                stats['not_saved'] += 1

            if not must_save:
                if new_occurence is not None:
                    #new_occurence['samples'] = np.array(new_occurence['samples'], bo.SAMPLE_TYPE)
                    new_occurences.append(new_occurence)
                    new_occurence = None

    print('stats', stats, new_occurences)

    return new_occurences



def combine_blocks(cursor, offset):
    occurences = get_occurences(cursor, offset)

    combined_data = np.zeros([1.3*CHUNK_SIZE], dtype = SAMPLE_TYPE)

    bo.sum_pulses(occurences, combined_data)
    peaks = 1 # signal.find_peaks_cwt(combined_data, np.array([100]))

    return occurences, peaks

    #import matplotlib.pyplot as plt
    #plt.plot(combined_data)
    #plt.vlines(peaks, ymin=0, ymax=plt.ylim()[1], colors='r', linestyles='dashed')
    #plt.savefig('output.eps')
    #plt.show()



import zlib, pickle

def zdumps(obj):
    return zlib.compress(pickle.dumps(obj,pickle.HIGHEST_PROTOCOL),9)

def zloads(zstr):
    return pickle.loads(zlib.decompress(zstr))

if __name__ == "__main__":
    c = pymongo.MongoClient()
    db = c.data
    collection = db.test

    BIG_NUMBER = 100000
    for i in range(BIG_NUMBER):
        t0 = i * CHUNK_SIZE
        t1 = (i+1) * CHUNK_SIZE
        query = {'triggertime' : {'$lt' : t1, '$gt' : t0}}

        results = collection.find(query)#, fields={ 'triggertime': 1, 'data':1, 'zipped':1, 'module':1, 'group':1 })
        #print(json.dumps(results.explain(), sort_keys=True, indent=4))
        print('indexOnly', results.explain())#['indexOnly'])

        print(results.count())
        occurences, peaks = combine_blocks(results, offset=(i * CHUNK_SIZE))

        new_doc = {}
        new_doc['t0'] = t0
        new_doc['t1'] = t1
        new_doc['occurences'] = occurences #zdumps(determine_data_to_store(occurences, peaks)) # (

        print(size, len(new_doc['occurences']))
        #db.saved.save(new_doc)




