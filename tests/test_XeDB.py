#!/usr/bin/env python

import unittest

from cito.core import XeDB


class TestXeDB(unittest.TestCase):

    def test_get_server_name(self):
        self.assertEqual(XeDB.get_server_name(), "127.0.0.1")

    def test_get_pymongo_collection(self):
        pass


if __name__ == '__main__':
    unittest.main()
