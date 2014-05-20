__author__ = 'tunnell'

import sys

import mongomock


sys.modules['pymongo'] = mongomock

import unittest
import pickle
import gzip

from tqdm import tqdm

from wax.Database import OutputDBInterface, InputDBInterface
from wax.EventBuilder.Processor import SingleThreaded
from wax.Configuration import PADDING


class TestOnGoodEvents(unittest.TestCase):

    def setUp(self):
        f = gzip.open('tests/test_data.pkl.gz', 'rb')
        pickle.load(f)
        self.answer = pickle.load(f)
        self.hostname = '127.0.0.1'
        self.dataset = 'dataset'
        self.input = InputDBInterface.MongoDBInput(collection_name=self.dataset,
                                                   hostname=self.hostname)
        self.output = OutputDBInterface.MongoDBOutput(collection_name=self.dataset,
                                                      hostname=self.hostname)

        while (1):
            try:
                print('.', end='')
                self.input.collection.insert(pickle.load(f))
            except Exception as e:
                print(e)
                break

        print('')

    def test_something(self):
        p = SingleThreaded(chunksize=10 ** 8,
                        padding=PADDING)
        p._initialize(hostname=self.hostname,
                      dataset=self.dataset)

        for i in range(15):
            print('i %d' % i)
            p.get_processing_function()(i * 10 ** 8, (i + 1) * 10 ** 8 + PADDING,
                                        hostname=self.hostname,
                                        collection_name=self.dataset)

        collection = self.output.get_collection()
        cursor = collection.find()
        ranges = []
        n = cursor.count()
        for i in tqdm(range(n)):
            event = next(cursor)
            ranges.append(event['range'])

        def check_in_range(time):
            for myrange in ranges:
                if myrange[0] < time < myrange[1]:
                    return True
            return False

        good = 0
        all_count = 0
        for value in self.answer:
            all_count += 1
            if check_in_range(value['time']):
                good += 1
            else:
                print('fail', value)

        self.assertGreaterEqual((float(good) / all_count), 1.0)


if __name__ == '__main__':
    unittest.main()
