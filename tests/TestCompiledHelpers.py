"""Tests of the C extensions to speed up event building.

This calls C code, which involves pointers and memory allocation; therefore,
it is very important to test this well.  Segmentation faults in this code
would be very hard to track down since the DAQ would just stop running.
"""
import unittest

import numpy as np

import ebcore


class CompiledHelpersTestCase(unittest.TestCase):

    def setUp(self):
        self.sample_type = np.int32

    def check(self, x, y, gap=1, offset=0, threshold=5):
        """Helper routine

        To avoid every test case having to set up the C module, add samples to
        it, then build events, we've provided a method that performs these
        common actions.
        """
        ebcore.Setup(100)

        x *= -1
        x += 16384
        ebcore.add_samples(x, offset, 1)

        y2 = ebcore.build_events(threshold, gap)

        self.assertEqual(len(y2), len(y))
        self.assertIsInstance(y2, np.ndarray)
        self.assertTrue(np.array_equal(y, y2),
                        "%s %s" % (str(y), str(y2)))
        del y2

    def test_single_pulse(self):
        """One signal above threshold"""
        x = np.array([0, 0, 0, 0, 10, 0, ], dtype=self.sample_type)
        y = np.array([3, 5], dtype=self.sample_type)
        self.check(x, y)

    # def test_offset(self):
    #     """Offset in add_samples"""
    #     x = np.array([0, 0, 0, 0, 10, 0, ], dtype=self.sample_type)
    #     y = np.array([6, 8], dtype=self.sample_type)
    #     self.check(x, y, offset=3)

    def test_double_pulse(self):
        """Double signal above threshold"""
        x = np.array([0, 0, 10, 0, 0, 10, 0, ], dtype=self.sample_type)
        y = np.array([1, 3, 4, 6], dtype=self.sample_type)
        self.check(x, y)

    def test_combine_pulse(self):
        """Double signal above threshold"""
        x = np.array([0, 0, 10, 0, 10, 0, ], dtype=self.sample_type)
        y = np.array([0, 6], dtype=self.sample_type)
        self.check(x, y, gap=2)

    def test_multiple_adding(self):
        """Multiple add samples"""
        cch.setup(10)

        x0 = np.array([0, 0, 0, 0, 10, 0, 0, 0, 0, 0], dtype=self.sample_type)
        x1 = -1 * x0 + 16384

        n = 5
        for i in range(n):
            cch.add_samples(x1.copy(), 0, 1)

        self.assertTrue(np.array_equal(cch.get_sum(),
                                       n * x0))

    def test_no_pulse(self):
        """No signal above threshold"""
        x = np.array([0, 0, 0, 0, 0, 0, ], dtype=self.sample_type)
        y = np.array([], dtype=self.sample_type)
        self.check(x, y)

    def test_overlap_simple(self):
        """Test event matching"""
        x = np.array([0, 0, 10, 0, 0, 10, 0, ], dtype=self.sample_type)
        y = np.array([1, 3, 4, 6], dtype=self.sample_type)
        self.check(x, y)

        self.assertTrue(np.array_equal(cch.overlaps(y), np.array([0, 1])))

        y = np.array([1, 3, 1, 3, 4, 6], dtype=self.sample_type)
        self.assertTrue(np.array_equal(cch.overlaps(y),
                                       np.array([0, 0, 1])))

    def test_overlap_complex_mid(self):
        """Test event matching where samples before events"""
        x = np.array([0, 10, 0, 0, 0, 0, 0, 0, 10, 0], dtype=self.sample_type)
        y = np.array([0, 2, 7, 9], dtype=self.sample_type)

        self.check(x, y)

        self.assertTrue(np.array_equal(cch.overlaps(y), np.array([0, 1])))

        y = np.array([3, 5], dtype=self.sample_type)

        self.assertTrue(np.array_equal(cch.overlaps(y),
                                       np.array([-1])))

    def test_overlap_complex_post(self):
        """Test event matching where samples after events"""
        x = np.array([0, 10, 0, 0, 0, 0, 0, 0, 0, 0], dtype=self.sample_type)
        y = np.array([0, 2, ], dtype=self.sample_type)

        self.check(x, y)

        self.assertTrue(np.array_equal(cch.overlaps(y), np.array([0])))

        y = np.array([7, 9], dtype=self.sample_type)
        self.assertTrue(np.array_equal(cch.overlaps(y),
                                       np.array([-1])))

    def test_overlap_complex_pre(self):
        """Test event matching where samples before events"""
        x = np.array([0, 0, 0, 0, 0, 10, 0, ], dtype=self.sample_type)
        y = np.array([4, 6], dtype=self.sample_type)
        self.check(x, y)

        self.assertTrue(np.array_equal(cch.overlaps(y), np.array([0])))

        y = np.array([0, 1], dtype=self.sample_type)

        self.assertTrue(np.array_equal(cch.overlaps(y),
                                       np.array([-1])))

    def __del__(self):
        pass  # cch.shutdown()


if __name__ == '__main__':
    unittest.main()
