#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_cito
----------------------------------

Tests for `cito` module.
"""

from cito.core import XeDB

XeDB.get_mongo_db_objects = XeDB.mock_get_mongo_db_objects

import unittest

from cito import main


class TestInspector(unittest.TestCase):
    def setUp(self):
        pass

    def test_process_ten_docs(self):
        myapp = main.CitoApp()
        myapp.run("process --debug -vvvv --num 10".split())

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
