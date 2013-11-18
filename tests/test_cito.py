#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_cito
----------------------------------

Tests for `cito` module.
"""

import unittest

from cito import main


class TestCito(unittest.TestCase):
    def setUp(self):
        pass

#    def test_something(self):
#        argv = "plot --chunksize 100000000 -vvvvvvvv --debug".split()
#        myapp = main.CitoApp()
#        print( myapp.run(argv))

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
