#!/usr/bin/env python

import unittest


from cito.EventBuilder import Output

import pickle


class TestOutputCommon(unittest.TestCase):

    def test_cannot_initialize(self):
        with self.assertRaises(ValueError):
            Output.OutputCommon()


class TestMongoDBOutput(unittest.TestCase):

    def setUp(self):
        self.c = Output.MongoDBOutput()
        #self.c.collection = mongomock.Connection()['output']['something']

        import inspect
        import os

        # script directory
        dir = os.path.dirname(
            os.path.abspath(inspect.getfile(inspect.currentframe())))

        self.f = open(os.path.join(dir, 'all_data.p'), 'rb')
        self.t0 = pickle.load(self.f)
        self.t1 = pickle.load(self.f)
        self.peaks = pickle.load(self.f)
        self.alldata = pickle.load(self.f)

    def test_evt_number(self):
        self.assertEqual(self.c.event_number, "Not set")

    def tearDown(self):
        self.f.close()


if __name__ == '__main__':
    unittest.main()