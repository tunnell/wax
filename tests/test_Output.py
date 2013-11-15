#!/usr/bin/env python

import unittest

import logging
import sys
from cito.core import Output
import pickle

class TestOutputCommon(unittest.TestCase):
    def test_cannot_initialize(self):
        with self.assertRaises(ValueError):
            Output.OutputCommon()



class TestMongoDBOutput(unittest.TestCase):
    def setUp(self):
        self.c = Output.MongoDBOutput()

        self.f = open('all_data.p', 'rb')

        self.t0 = pickle.load(self.f)
        self.t1 = pickle.load(self.f)
        self.peaks = pickle.load(self.f)
        self.alldata = pickle.load(self.f)


    def test_something(self):
        print(self.alldata)
        print(self.c.write_data_range(self.t0, self.t1, self.alldata, self.peaks, save_range=100))

    def tearDown(self):
        self.f.close()


class TestHDF5Output(unittest.TestCase):
    def setUp(self):
        pass

    def test_something(self):
        pass


class EpsOutput(unittest.TestCase):
    def setUp(self):
        self.c = Output.EpsOutput()

        self.f = open('all_data.p', 'rb')

        self.t0 = pickle.load(self.f)
        self.t1 = pickle.load(self.f)
        self.peaks = pickle.load(self.f)
        self.alldata = pickle.load(self.f)

    def test_something(self):
        print(self.alldata)
        print(self.c.write_data_range(self.t0, self.t1, self.alldata, self.peaks, save_range=100))




if __name__ == '__main__':
    logging.basicConfig( stream=sys.stderr )
    logging.getLogger( "OutputCommon" ).setLevel( logging.DEBUG )
    unittest.main()
