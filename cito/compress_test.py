import pymongo
import blosc
import numpy as np
import snappy
import zlib

#if current_channel not in results:
# Samples are actually 14 bit
SAMPLE_TYPE = np.uint16

c = pymongo.MongoClient()
db = c.data
collection = db.test

for doc in collection.find():
    data = doc['data']

    if doc['zipped']:
        data = snappy.uncompress(data)
    print("Diagnostics")
    print("\traw:", len(data))
    print("\tsnappy:", len(snappy.compress(data)))
    print("\tblosc:", len(blosc.compress(data, typesize=8)))
    print("\tzlib:", len(zlib.compress(data)))

