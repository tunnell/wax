#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_cito
----------------------------------

Tests for `cito` module.
"""

import unittest

from cito.core import InterfaceV1724
from cito.core import XeDB


class TestInterface1724(unittest.TestCase):
    def test_good_data(self):
        x = {'triggertime': 9226060, 'datalength': 208, 'zipped': False, 'module': 33, 'data': b'\x84>\x81>\x84>\x83>\x81>\x80>\x85>\x83>\x82>\x85>\x84>\x81>\x85>\x83>\x83>\x85>\x84>\x87>\x81>\x82>\x84>\x83>\x82>\x85>\x84>\x83>\x80>\x82>\x84>\x82>\x83>\x80>\x81>\x82>\x83>\x82>\x81>\x83>\x84>\x84>\x81>\x82>\x84>\x82>\x83>\x83>\x83>\x81>\x83>\x83>\x81>\n>S>s>\x81>\x81>\x82>\x84>\x83>\x83>\x82>\x83>\x81>\x81>\x80>\x82>\x82>\x82>\x83>\x80>\x80>\x81>\x81>\x83>\x83>\x84>\x82>\x82>\x84>\x83>\x82>\x81>\x83>\x82>\x83>\x82>\x81>\x82>\x80>\x83>\x84>\x81>\x83>\x83>\x85>\x84>\x81>\x81>\x82>\x7f>\x7f>\x80>\x80>\x82>',
             'insertsize': 1}
        data = XeDB.get_data_from_doc(x)
        print(InterfaceV1724.get_samples(data))


if __name__ == '__main__':
    unittest.main()
