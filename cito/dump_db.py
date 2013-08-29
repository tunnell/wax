__author__ = 'tunnell'

import pymongo

c = pymongo.MongoClient('130.92.139.92')
c['data'].drop_collection('test')