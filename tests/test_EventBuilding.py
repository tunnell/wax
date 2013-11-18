#!/usr/bin/env python

import unittest

import numpy as np
from cito.EventBuilder import EventBuilding


class Test_split_boolean_array(unittest.TestCase):

    def setUp(self):
        self.answer = {}
        self.answer[(True, True, True)] = [(0, 3)]
        self.answer[(True, True, False)] = [(0, 2)]
        self.answer[(True, False, True)] = [(0, 1), (2, 3)]
        self.answer[(True, False, False)] = [(0, 1)]
        self.answer[(False, True, True)] = [(1, 3)]
        self.answer[(False, True, False)] = [(1, 2)]
        self.answer[(False, False, True)] = [(2, 3)]
        self.answer[(False, False, False)] = []

    def test_length3(self):
        f = EventBuilding.split_boolean_array
        for i in [True, False]:
            for j in [True, False]:
                for k in [True, False]:
                    self.assertEqual(f(np.array((i, j, k), dtype=np.bool)),
                                     self.answer[(i, j, k)])

    def test_length6(self):
        f = EventBuilding.split_boolean_array
        for i in [True, False]:
            for j in [True, False]:
                for k in [True, False]:
                    new_answer = [(2 * a, 2 * b)
                                  for a, b in self.answer[(i, j, k)]]
                    self.assertEqual(
                        f(np.array((i, i, j, j, k, k), dtype=np.bool)),
                        new_answer)


class Test_save_time_range(unittest.TestCase):

    def setUp(self):
        self.single = [False, False,  True,  True,
                       True,  True,  True,  True, False, False]
        self.range_around_trigger = (-3, 3)

    def test_single_peak_int(self):
        x = EventBuilding.get_index_mask_for_trigger(
            10, 5, self.range_around_trigger).tolist()
        self.assertEqual(self.single,
                         x)

    def test_single_peak_list(self):
        x = EventBuilding.get_index_mask_for_trigger(
            10, 5, self.range_around_trigger).tolist()
        self.assertEqual(self.single,
                         x)

    def test_multi_peak_list_no_overlap(self):
        x = EventBuilding.get_index_mask_for_trigger(
            10, [2, 9], self.range_around_trigger).tolist()
        self.assertEqual(
            [True, True, True, True, True, False, True, True, True, True],
            x)

    def test_multi_peak_list_overlap(self):
        x = EventBuilding.get_index_mask_for_trigger(
            10, [5, 15], self.range_around_trigger).tolist()
        self.assertEqual(self.single,
                         x)

    def test_overrun(self):
        x = EventBuilding.get_index_mask_for_trigger(
            10, [0], self.range_around_trigger).tolist()
        self.assertEqual(
            [True, True, True, False, False,
                False, False, False, False, False],
            x)

    def test_single_peak_float_exception(self):
        with self.assertRaises(ValueError):
            EventBuilding.get_index_mask_for_trigger(
                10, 5.0, self.range_around_trigger)

    def test_size_not_int(self):
        with self.assertRaises(ValueError):
            EventBuilding.get_index_mask_for_trigger(
                [10], 5, self.range_around_trigger)


class Test_save_time_range(unittest.TestCase):

    def setUp(self):
        self.single = [False, False,  True,  True,
                       True,  True,  True,  True, False, False]
        self.range_around_trigger = (-3, 3)

    def test_single_peak_int(self):
        x = EventBuilding.get_index_mask_for_trigger(
            10, 5, self.range_around_trigger).tolist()
        self.assertEqual(self.single,
                         x)

    def test_single_peak_list(self):
        x = EventBuilding.get_index_mask_for_trigger(
            10, 5, self.range_around_trigger).tolist()
        self.assertEqual(self.single,
                         x)

    def test_multi_peak_list_no_overlap(self):
        x = EventBuilding.get_index_mask_for_trigger(
            10, [2, 9], self.range_around_trigger).tolist()
        self.assertEqual(
            [True, True, True, True, True, False, True, True, True, True],
            x)

    def test_multi_peak_list_overlap(self):
        x = EventBuilding.get_index_mask_for_trigger(
            10, [5, 15], self.range_around_trigger).tolist()
        self.assertEqual(self.single,
                         x)

    def test_overrun(self):
        x = EventBuilding.get_index_mask_for_trigger(
            10, [0], self.range_around_trigger).tolist()
        self.assertEqual(
            [True, True, True, False, False,
                False, False, False, False, False],
            x)

    def test_single_peak_float_exception(self):
        with self.assertRaises(ValueError):
            EventBuilding.get_index_mask_for_trigger(
                10, 5.0, self.range_around_trigger)

    def test_size_not_int(self):
        with self.assertRaises(ValueError):
            EventBuilding.get_index_mask_for_trigger(
                [10], 5, self.range_around_trigger)


if __name__ == '__main__':
    unittest.main()
