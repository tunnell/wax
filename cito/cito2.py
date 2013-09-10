#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymongo

from pint import UnitRegistry
ureg = UnitRegistry()

# One sample of the v1724 ADC is 10 ns.
ureg.define('sample =  10 * nanosecond')

# There are 31 bits for time on our v1724, so a group refers to when the clock
# wraps around.
ureg.define('group = 2^31 * sample')

Q_ = ureg.Quantity


def get_default_collection():
    c = pymongo.MongoClient()
    db = c.data
    collection = db.test
    return collection
