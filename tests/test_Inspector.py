#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_cito
----------------------------------

Tests for `cito` module.
"""

import unittest

from cito.core import XeDB
XeDB.get_mongo_db_objects = XeDB.mock_get_mongo_db_objects

from cito import main

class TestInspector(unittest.TestCase):
    def setUp(self):
        pass

    def test_default_requires_args(self):
        myapp = main.CitoApp()
        with self.assertRaises(SystemExit) as cm:
            myapp.run("doc inspector".split())

    def test_random_doc(self):
        myapp = main.CitoApp()
        myapp.run("doc inspector -r".split())

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
